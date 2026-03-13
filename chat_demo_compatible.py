#!/usr/bin/env python3
"""
seekdb聊天Demo - 兼容版本
使用SQLite + 模拟向量功能，展示seekdb的设计理念
"""

import os
import json
import datetime
import sqlite3
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ChatMessage:
    """聊天消息数据模型"""
    id: Optional[int] = None
    role: str = ""  # user, assistant, system
    content: str = ""
    timestamp: Optional[datetime.datetime] = None
    session_id: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()
        if self.metadata is None:
            self.metadata = {}


class MockSeekDBChat:
    """seekdb聊天系统兼容版本
    使用SQLite + 简单文本匹配模拟seekdb的混合搜索功能
    """
    
    def __init__(self, db_path: str = "./chat_demo.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.conn = None
        
        # 模拟知识库
        self.mock_knowledge = [
            {
                "title": "什么是seekdb？",
                "content": "seekdb是OceanBase推出的AI原生混合搜索数据库，融合向量、文本、结构化数据能力，支持多模混合搜索与智能推理。",
                "category": "产品介绍",
                "tags": ["seekdb", "数据库", "AI", "混合搜索"]
            },
            {
                "title": "混合搜索技术",
                "content": "混合搜索结合向量搜索（语义理解）和全文搜索（关键词匹配），提供更精准的搜索结果。seekdb内置支持这种混合搜索模式。",
                "category": "技术概念",
                "tags": ["混合搜索", "向量搜索", "全文搜索", "技术"]
            },
            {
                "title": "RAG技术介绍",
                "content": "RAG（Retrieval-Augmented Generation）通过检索相关知识增强AI生成的准确性和相关性，是seekdb的核心应用场景之一。",
                "category": "技术概念",
                "tags": ["RAG", "检索增强", "AI生成", "知识库"]
            },
            {
                "title": "seekdb的AI函数",
                "content": """seekdb提供强大的AI函数：
- AI_EMBED: 文本转向量嵌入
- AI_COMPLETE: 文本生成
- AI_RERANK: 结果重排序
- 支持实时推理和智能分析""",
                "category": "功能特性",
                "tags": ["AI函数", "嵌入", "生成", "推理"]
            },
            {
                "title": "如何开始使用seekdb？",
                "content": """开始使用seekdb的步骤：
1. 安装：pip install seekdb
2. 连接：seekdb.connect('database.db')
3. 创建表：支持向量字段和AI函数
4. 插入数据：自动生成向量嵌入
5. 查询：支持混合搜索和AI推理""",
                "category": "使用指南",
                "tags": ["安装", "使用", "教程", "入门"]
            }
        ]
        
        self.init_database()
    
    def init_database(self):
        """初始化数据库和表结构"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            
            # 创建聊天消息表
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL,
                    metadata TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    gmt_create DATETIME DEFAULT CURRENT_TIMESTAMP,
                    gmt_modified DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建知识库表
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    category TEXT,
                    tags TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    gmt_create DATETIME DEFAULT CURRENT_TIMESTAMP,
                    gmt_modified DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON chat_messages(session_id)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category)")
            
            # 检查是否需要初始化知识库
            count = self.conn.execute("SELECT COUNT(*) FROM knowledge_base WHERE is_deleted = 0").fetchone()[0]
            if count == 0:
                self._init_knowledge_base()
            
            self.conn.commit()
            print("✅ 兼容版数据库初始化成功")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
    
    def _init_knowledge_base(self):
        """初始化知识库"""
        for item in self.mock_knowledge:
            self.add_knowledge(
                title=item["title"],
                content=item["content"],
                category=item["category"],
                tags=item["tags"]
            )
    
    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """简单的文本相似度计算"""
        # 使用Jaccard相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)
    
    def _keyword_match(self, query: str, text: str) -> float:
        """关键词匹配"""
        query_words = query.lower().split()
        text_lower = text.lower()
        
        matches = sum(1 for word in query_words if word in text_lower)
        return matches / len(query_words) if query_words else 0.0
    
    def add_message(self, message: ChatMessage) -> int:
        """添加聊天消息"""
        try:
            sql = """
                INSERT INTO chat_messages (role, content, session_id, metadata)
                VALUES (?, ?, ?, ?)
            """
            cursor = self.conn.execute(sql, [
                message.role,
                message.content,
                message.session_id,
                json.dumps(message.metadata)
            ])
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ 添加消息失败: {e}")
            return -1
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """获取聊天历史"""
        try:
            sql = """
                SELECT id, role, content, timestamp, session_id, metadata
                FROM chat_messages
                WHERE session_id = ? AND is_deleted = 0
                ORDER BY timestamp ASC
                LIMIT ?
            """
            results = self.conn.execute(sql, [session_id, limit]).fetchall()
            
            messages = []
            for row in results:
                messages.append(ChatMessage(
                    id=row[0],
                    role=row[1],
                    content=row[2],
                    timestamp=datetime.datetime.fromisoformat(row[3]),
                    session_id=row[4],
                    metadata=json.loads(row[5]) if row[5] else {}
                ))
            return messages
        except Exception as e:
            print(f"❌ 获取聊天记录失败: {e}")
            return []
    
    def add_knowledge(self, title: str, content: str, category: str = "general", tags: List[str] = None):
        """添加知识到知识库"""
        try:
            if tags is None:
                tags = []
            
            sql = """
                INSERT INTO knowledge_base (title, content, category, tags)
                VALUES (?, ?, ?, ?)
            """
            self.conn.execute(sql, [title, content, category, json.dumps(tags)])
            self.conn.commit()
            print(f"✅ 知识已添加: {title}")
        except Exception as e:
            print(f"❌ 添加知识失败: {e}")
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """搜索相关知识（模拟混合搜索）"""
        try:
            # 获取所有知识
            sql = "SELECT title, content, category, tags FROM knowledge_base WHERE is_deleted = 0"
            results = self.conn.execute(sql).fetchall()
            
            # 计算相关性得分
            scored_results = []
            for row in results:
                title, content, category, tags = row
                
                # 组合文本进行搜索
                full_text = f"{title} {content} {category} {' '.join(json.loads(tags))}"
                
                # 计算相似度（文本相似度 + 关键词匹配）
                text_sim = self._simple_text_similarity(query, full_text)
                keyword_sim = self._keyword_match(query, full_text)
                
                # 综合得分
                combined_score = (text_sim + keyword_sim) / 2
                
                if combined_score > 0.1:  # 阈值过滤
                    scored_results.append({
                        "title": title,
                        "content": content,
                        "category": category,
                        "tags": json.loads(tags) if tags else [],
                        "score": combined_score
                    })
            
            # 按得分排序
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            return scored_results[:limit]
            
        except Exception as e:
            print(f"❌ 搜索知识失败: {e}")
            return []
    
    def generate_response(self, user_input: str, session_id: str) -> str:
        """生成AI回复（模拟AI功能）"""
        try:
            # 获取聊天历史作为上下文
            history = self.get_chat_history(session_id, limit=10)
            
            # 搜索相关知识
            relevant_knowledge = self.search_knowledge(user_input)
            
            # 构建回复
            response_parts = []
            
            # 根据用户输入生成回复
            user_lower = user_input.lower()
            
            # 处理常见问题
            if any(word in user_lower for word in ["你好", "hi", "hello"]):
                response_parts.append("你好！我是基于seekdb的AI助手，很高兴为你服务。我可以回答关于seekdb的问题，也可以进行日常对话。")
            
            elif any(word in user_lower for word in ["seekdb", "seek db"]):
                if relevant_knowledge:
                    response_parts.append(f"关于seekdb，我可以分享以下信息：")
                    for item in relevant_knowledge[:2]:
                        response_parts.append(f"• {item['title']}: {item['content'][:150]}...")
                else:
                    response_parts.append("seekdb是OceanBase推出的AI原生混合搜索数据库，支持向量、文本、结构化数据的统一处理。")
            
            elif any(word in user_lower for word in ["混合搜索", "向量搜索"]):
                response_parts.append("混合搜索是seekdb的核心特性之一，它结合了向量搜索的语义理解能力和全文搜索的关键词匹配能力，提供更精准的搜索结果。")
            
            elif any(word in user_lower for word in ["rag", "检索增强"]):
                response_parts.append("RAG（Retrieval-Augmented Generation）技术通过检索相关知识来增强AI生成的准确性和相关性。seekdb内置支持这种技术。")
            
            elif any(word in user_lower for word in ["安装", "使用", "教程"]):
                response_parts.append("使用seekdb非常简单：1) 安装：pip install seekdb 2) 连接：seekdb.connect('database.db') 3) 使用标准SQL操作")
            
            else:
                # 基于相关知识生成回复
                if relevant_knowledge:
                    best_match = relevant_knowledge[0]
                    response_parts.append(f"基于我的知识库，关于'{user_input}'，我想分享：")
                    response_parts.append(best_match['content'])
                else:
                    # 通用回复
                    response_parts.append(f"你提到'{user_input}'，作为一个AI助手，我很乐意讨论这个话题。")
                    if history:
                        response_parts.append("我们之前的对话让我了解到你对此很感兴趣。继续聊聊吧！")
            
            # 添加友好结尾
            response_parts.append("有什么其他问题我可以帮你解答吗？")
            
            return "\n\n".join(response_parts)
            
        except Exception as e:
            print(f"❌ 生成回复失败: {e}")
            return "抱歉，我遇到了一些问题，请稍后再试。"
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # 测试兼容版seekdb聊天系统
    print("🤖 启动seekdb兼容版聊天Demo...")
    chat = MockSeekDBChat()
    
    print("\n🎯 测试功能:")
    print("- 搜索知识库")
    results = chat.search_knowledge("seekdb是什么")
    for item in results:
        print(f"  {item['title']}: {item['content'][:100]}...")
    
    print("\n- 开始对话测试...")
    session_id = "demo_session"
    
    test_inputs = [
        "你好",
        "seekdb是什么？",
        "混合搜索有什么优势？",
        "如何使用seekdb进行开发？",
        "谢谢你的回答"
    ]
    
    for user_input in test_inputs:
        print(f"\n👤 用户: {user_input}")
        response = chat.generate_response(user_input, session_id)
        print(f"🤖 AI: {response}")
        
        # 保存消息
        user_msg = ChatMessage(role="user", content=user_input, session_id=session_id)
        chat.add_message(user_msg)
        
        ai_msg = ChatMessage(role="assistant", content=response, session_id=session_id)
        chat.add_message(ai_msg)
    
    print("\n✅ 测试完成！")
    chat.close()
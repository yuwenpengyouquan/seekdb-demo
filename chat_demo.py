#!/usr/bin/env python3
"""
seekdb 聊天Demo应用 - 主应用文件
基于seekdb的AI原生混合搜索能力构建RAG聊天系统
"""

import os
import json
import datetime
from typing import List, Dict, Optional
import seekdb
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


class SeekDBChat:
    """seekdb聊天系统核心类"""
    
    def __init__(self, db_path: str = "./chat_demo.db"):
        """初始化seekdb连接"""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库和表结构"""
        try:
            # 连接seekdb
            self.conn = seekdb.connect(self.db_path)
            
            # 创建聊天消息表
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id VARCHAR(100) NOT NULL,
                    metadata JSON,
                    embedding VECTOR(384),  -- 文本向量嵌入
                    is_deleted TINYINT(1) DEFAULT 0,
                    gmt_create DATETIME DEFAULT CURRENT_TIMESTAMP,
                    gmt_modified DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建知识库表用于RAG
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(500),
                    content TEXT NOT NULL,
                    category VARCHAR(100),
                    tags JSON,
                    embedding VECTOR(384),
                    is_deleted TINYINT(1) DEFAULT 0,
                    gmt_create DATETIME DEFAULT CURRENT_TIMESTAMP,
                    gmt_modified DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建向量索引
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_embedding ON chat_messages USING HNSW (embedding)
            """)
            
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base USING HNSW (embedding)
            """)
            
            # 创建全文索引
            self.conn.execute("""
                CREATE FULLTEXT INDEX IF NOT EXISTS idx_chat_content ON chat_messages(content)
            """)
            
            self.conn.execute("""
                CREATE FULLTEXT INDEX IF NOT EXISTS idx_knowledge_content ON knowledge_base(content)
            """)
            
            print("✅ seekdb数据库初始化成功")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
    
    def add_message(self, message: ChatMessage) -> int:
        """添加聊天消息"""
        try:
            # 生成文本嵌入
            embedding_sql = "SELECT AI_EMBED(?) as embedding"
            embedding_result = self.conn.execute(embedding_sql, [message.content])
            embedding = embedding_result.fetchone()[0]
            
            sql = """
                INSERT INTO chat_messages (role, content, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor = self.conn.execute(sql, [
                message.role, 
                message.content, 
                message.session_id,
                json.dumps(message.metadata),
                embedding
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
                    timestamp=row[3],
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
            
            # 生成文本嵌入
            embedding_sql = "SELECT AI_EMBED(?) as embedding"
            embedding_result = self.conn.execute(embedding_sql, [content])
            embedding = embedding_result.fetchone()[0]
            
            sql = """
                INSERT INTO knowledge_base (title, content, category, tags, embedding)
                VALUES (?, ?, ?, ?, ?)
            """
            self.conn.execute(sql, [
                title, content, category, json.dumps(tags), embedding
            ])
            self.conn.commit()
            print(f"✅ 知识已添加: {title}")
        except Exception as e:
            print(f"❌ 添加知识失败: {e}")
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """搜索相关知识"""
        try:
            # 生成查询嵌入
            embedding_sql = "SELECT AI_EMBED(?) as embedding"
            embedding_result = self.conn.execute(embedding_sql, [query])
            query_embedding = embedding_result.fetchone()[0]
            
            # 向量搜索 + 全文搜索的混合搜索
            sql = """
                SELECT title, content, category, tags, 
                       VECTOR_DISTANCE(embedding, ?) as distance
                FROM knowledge_base
                WHERE is_deleted = 0
                ORDER BY distance ASC
                LIMIT ?
            """
            results = self.conn.execute(sql, [query_embedding, limit]).fetchall()
            
            knowledge = []
            for row in results:
                knowledge.append({
                    "title": row[0],
                    "content": row[1],
                    "category": row[2],
                    "tags": json.loads(row[3]) if row[3] else [],
                    "distance": row[4]
                })
            return knowledge
        except Exception as e:
            print(f"❌ 搜索知识失败: {e}")
            return []
    
    def generate_response(self, user_input: str, session_id: str) -> str:
        """生成AI回复"""
        try:
            # 获取聊天历史作为上下文
            history = self.get_chat_history(session_id, limit=10)
            
            # 搜索相关知识
            relevant_knowledge = self.search_knowledge(user_input)
            
            # 构建提示
            context_parts = []
            if relevant_knowledge:
                context_parts.append("相关知识点:")
                for item in relevant_knowledge[:3]:
                    context_parts.append(f"- {item['title']}: {item['content'][:200]}...")
            
            history_parts = []
            for msg in history[-6:]:  # 最近6条消息
                history_parts.append(f"{msg.role}: {msg.content}")
            
            prompt = f"""
            你是一个有帮助的AI助手，基于以下知识回答用户问题。
            
            {chr(10).join(context_parts)}
            
            最近的对话历史:
            {chr(10).join(history_parts)}
            
            用户: {user_input}
            助手:
            """
            
            # 使用AI_COMPLETE生成回复
            ai_sql = "SELECT AI_COMPLETE(?) as response"
            result = self.conn.execute(ai_sql, [prompt])
            response = result.fetchone()[0]
            
            return response
        except Exception as e:
            print(f"❌ 生成回复失败: {e}")
            return "抱歉，我遇到了一些问题，请稍后再试。"
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # 测试seekdb聊天系统
    chat = SeekDBChat()
    
    # 添加一些示例知识
    chat.add_knowledge(
        "seekdb介绍", 
        "seekdb是OceanBase推出的AI原生混合搜索数据库，支持向量、文本、结构化数据的统一处理。",
        "产品介绍"
    )
    
    chat.add_knowledge(
        "向量搜索", 
        "向量搜索是通过将文本转换为高维向量，计算向量间的相似度来实现语义搜索的技术。",
        "技术概念"
    )
    
    # 测试对话
    session_id = "demo_session"
    
    while True:
        user_input = input("\n你: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            break
            
        # 添加用户消息
        user_msg = ChatMessage(role="user", content=user_input, session_id=session_id)
        chat.add_message(user_msg)
        
        # 生成回复
        response = chat.generate_response(user_input, session_id)
        print(f"AI: {response}")
        
        # 添加AI回复
        ai_msg = ChatMessage(role="assistant", content=response, session_id=session_id)
        chat.add_message(ai_msg)
    
    chat.close()
    print("聊天已结束")

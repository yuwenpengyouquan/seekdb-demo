#!/usr/bin/env python3
"""
seekdb聊天Demo - 知识管理工具
用于管理和扩展聊天机器人的知识库
"""

import json
import argparse
from chat_demo import SeekDBChat


class KnowledgeManager:
    """知识库管理工具"""
    
    def __init__(self):
        self.chat = SeekDBChat()
    
    def add_sample_knowledge(self):
        """添加示例知识"""
        sample_knowledge = [
            {
                "title": "什么是混合搜索？",
                "content": "混合搜索是将向量搜索（基于语义）和全文搜索（基于关键词）结合起来的一种搜索技术。seekdb支持在一次查询中同时执行向量和全文搜索，提供更精准的搜索结果。",
                "category": "技术概念",
                "tags": ["混合搜索", "向量搜索", "全文搜索"]
            },
            {
                "title": "seekdb的AI函数",
                "content": """seekdb提供以下AI函数：
- AI_EMBED(text): 将文本转换为向量嵌入
- AI_COMPLETE(prompt): 基于提示生成文本
- AI_RERANK(query, docs): 对文档进行重排序
- DBMS_AI_SERVICE: 管理AI模型服务""",
                "category": "API文档",
                "tags": ["AI函数", "嵌入", "生成", "重排序"]
            },
            {
                "title": "RAG技术原理",
                "content": "RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI技术。它先从知识库中检索相关信息，然后基于这些信息生成回答，从而提高回答的准确性和相关性。",
                "category": "技术概念",
                "tags": ["RAG", "检索", "生成", "AI"]
            },
            {
                "title": "如何使用seekdb进行开发？",
                "content": """使用seekdb进行开发的步骤：
1. 安装：pip install seekdb
2. 连接：conn = seekdb.connect('database.db')
3. 创建表：使用标准SQL创建包含向量字段的表
4. 插入数据：使用AI_EMBED生成向量嵌入
5. 查询：使用向量距离函数进行相似性搜索""",
                "category": "开发指南",
                "tags": ["开发", "教程", "Python", "SQL"]
            }
        ]
        
        for item in sample_knowledge:
            self.chat.add_knowledge(
                title=item["title"],
                content=item["content"],
                category=item["category"],
                tags=item["tags"]
            )
        print("✅ 示例知识已添加")
    
    def search_knowledge(self, query: str, limit: int = 5):
        """搜索知识"""
        results = self.chat.search_knowledge(query, limit)
        if results:
            print(f"\n🔍 搜索结果: '{query}'")
            print("-" * 50)
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']} ({result['category']})")
                print(f"   相似度: {1-result['distance']:.2f}")
                print(f"   内容: {result['content'][:100]}...")
                print(f"   标签: {', '.join(result['tags'])}")
                print()
        else:
            print("❌ 未找到相关知识")
    
    def list_knowledge(self, category: str = None):
        """列出所有知识"""
        try:
            sql = "SELECT title, content, category, tags FROM knowledge_base WHERE is_deleted = 0"
            params = []
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            sql += " ORDER BY gmt_create DESC"
            
            results = self.chat.conn.execute(sql, params).fetchall()
            
            if results:
                print(f"\n📚 知识库 ({len(results)}条)")
                print("-" * 50)
                for title, content, cat, tags in results:
                    tags_list = json.loads(tags) if tags else []
                    print(f"📖 {title}")
                    print(f"   分类: {cat}")
                    print(f"   标签: {', '.join(tags_list)}")
                    print(f"   内容: {content[:150]}...")
                    print()
            else:
                print("📭 知识库为空")
        except Exception as e:
            print(f"❌ 查询失败: {e}")
    
    def delete_knowledge(self, title: str):
        """删除知识（软删除）"""
        try:
            sql = "UPDATE knowledge_base SET is_deleted = 1 WHERE title = ?"
            self.chat.conn.execute(sql, [title])
            self.chat.conn.commit()
            print(f"✅ 已删除知识: {title}")
        except Exception as e:
            print(f"❌ 删除失败: {e}")
    
    def interactive_mode(self):
        """交互式管理模式"""
        print("\n🎮 seekdb知识库管理工具")
        print("=" * 40)
        
        while True:
            print("\n可用命令:")
            print("1. add_sample - 添加示例知识")
            print("2. search [查询词] - 搜索知识")
            print("3. list [分类] - 列出知识")
            print("4. delete [标题] - 删除知识")
            print("5. exit - 退出")
            
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "add_sample":
                    self.add_sample_knowledge()
                
                elif cmd == "search":
                    query = " ".join(command[1:]) if len(command) > 1 else input("搜索词: ")
                    if query:
                        self.search_knowledge(query)
                
                elif cmd == "list":
                    category = command[1] if len(command) > 1 else None
                    self.list_knowledge(category)
                
                elif cmd == "delete":
                    title = " ".join(command[1:]) if len(command) > 1 else input("标题: ")
                    if title:
                        self.delete_knowledge(title)
                
                elif cmd in ["exit", "quit", "退出"]:
                    print("👋 再见！")
                    break
                
                else:
                    print("❌ 无效命令")
            
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        self.chat.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="seekdb知识库管理工具")
    parser.add_argument("command", choices=["add_sample", "search", "list", "interactive"], 
                       help="要执行的命令")
    parser.add_argument("--query", help="搜索查询词")
    parser.add_argument("--category", help="知识分类")
    parser.add_argument("--title", help="知识标题")
    
    args = parser.parse_args()
    
    manager = KnowledgeManager()
    
    try:
        if args.command == "add_sample":
            manager.add_sample_knowledge()
        
        elif args.command == "search":
            query = args.query or input("搜索词: ")
            manager.search_knowledge(query)
        
        elif args.command == "list":
            manager.list_knowledge(args.category)
        
        elif args.command == "interactive":
            manager.interactive_mode()
    
    finally:
        manager.chat.close()


if __name__ == "__main__":
    main()

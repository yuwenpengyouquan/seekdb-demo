#!/usr/bin/env python3
"""
seekdb AI知识库管理 - 高级版本
支持批量导入、智能标签、高级搜索
"""

import json
import os
import uuid
from typing import List, Dict
from chat_demo_compatible import MockSeekDBChat


class AdvancedKnowledgeManager:
    """高级知识库管理器"""
    
    def __init__(self):
        self.chat = MockSeekDBChat()
        self.setup_advanced_knowledge()
    
    def setup_advanced_knowledge(self):
        """设置高级知识库"""
        advanced_knowledge = [
            {
                "title": "seekdb架构深度解析",
                "content": """seekdb采用三层架构设计：
1. **存储引擎层**：基于LSM-Tree的存储引擎，支持ACID事务
2. **AI计算层**：内置AI_EMBED、AI_COMPLETE等函数，支持实时推理
3. **查询优化层**：混合搜索优化器，自动选择最优执行计划

技术特点：
- 向量索引：HNSW图索引，支持百万级向量检索
- 全文索引：BM25算法，支持中文分词
- 混合搜索：基于RRF的融合排序算法
- 实时更新：支持增量索引更新，毫秒级延迟""",
                "category": "技术架构",
                "tags": ["架构", "LSM-Tree", "AI函数", "混合搜索"],
                "difficulty": "高级",
                "author": "seekdb团队"
            },
            {
                "title": "RAG最佳实践指南",
                "content": """基于seekdb的RAG系统最佳实践：

**1. 知识准备**
- 文档分块策略：按语义分块，每块200-500字
- 元数据设计：包含标题、作者、时间戳、标签等
- 质量评估：使用BLEU、ROUGE等指标评估

**2. 检索优化**
- 混合权重：向量权重0.7，全文权重0.3
- 重排序策略：使用AI_RERANK进行二次排序
- 过滤条件：时间、作者、标签等多维度过滤

**3. 生成优化**
- Prompt模板：包含上下文、指令、格式要求
- 温度参数：0.7平衡创造性和准确性
- 最大长度：控制在500-800字符""",
                "category": "最佳实践",
                "tags": ["RAG", "检索优化", "生成优化", "实践指南"],
                "difficulty": "中级",
                "author": "AI团队"
            },
            {
                "title": "性能调优秘籍",
                "content": """seekdb性能调优完整指南：

**硬件优化**
- CPU：推荐8核以上，支持AVX指令集
- 内存：32GB起步，向量索引需要大量内存
- 存储：SSD推荐，NVMe更佳

**配置优化**
- 缓存配置：查询缓存256MB，连接池100连接
- 索引参数：HNSW M=16, ef_construction=200
- 并发设置：读写分离，主从复制

**查询优化**
- 预处理：使用AI_EMBED预计算向量
- 批处理：批量插入，减少IO开销
- 监控指标：QPS、延迟、内存使用率""",
                "category": "性能优化",
                "tags": ["性能", "调优", "硬件", "配置"],
                "difficulty": "高级",
                "author": "性能团队"
            },
            {
                "title": "企业级部署方案",
                "content": """seekdb企业级部署架构：

**高可用架构**
- 主从复制：一主多从，读写分离
- 负载均衡：基于权重的请求分发
- 故障转移：自动切换，秒级恢复

**安全策略**
- 访问控制：基于角色的权限管理
- 数据加密：传输加密+存储加密
- 审计日志：完整的操作记录

**监控告警**
- 性能监控：Prometheus + Grafana
- 日志分析：ELK Stack
- 告警机制：钉钉、企业微信通知""",
                "category": "企业部署",
                "tags": ["部署", "高可用", "安全", "监控"],
                "difficulty": "高级",
                "author": "运维团队"
            },
            {
                "title": "行业应用案例",
                "content": """seekdb在各行业的成功应用：

**智能客服**
- 场景：电商客服、技术支持
- 效果：响应时间<1秒，准确率95%+
- 特色：7x24小时服务，多轮对话

**知识管理**
- 场景：企业内部知识库、文档管理
- 效果：搜索效率提升300%，知识复用率80%+
- 特色：权限控制，版本管理

**教育培训**
- 场景：在线教育、智能答疑
- 效果：学生满意度90%+，教师效率提升50%
- 特色：个性化推荐，学习路径跟踪""",
                "category": "应用案例",
                "tags": ["客服", "知识管理", "教育", "案例"],
                "difficulty": "中级",
                "author": "解决方案团队"
            }
        ]
        
        for item in advanced_knowledge:
            self.chat.add_knowledge(
                title=item["title"],
                content=item["content"],
                category=item["category"],
                tags=item["tags"]
            )
        print("✅ 高级知识库已初始化")
    
    def import_from_file(self, filepath: str, category: str = "imported"):
        """从文件导入知识"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            filename = os.path.basename(filepath)
            self.chat.add_knowledge(
                title=f"导入文件: {filename}",
                content=content,
                category=category,
                tags=["导入", filename.split('.')[-1]]
            )
            print(f"✅ 已导入文件: {filename}")
            
        except Exception as e:
            print(f"❌ 导入失败: {e}")
    
    def search_with_filters(self, query: str, category: str = None, tags: List[str] = None, limit: int = 10) -> List[Dict]:
        """高级搜索功能"""
        results = self.chat.search_knowledge(query, limit * 2)
        
        filtered = []
        for item in results:
            if category and item['category'] != category:
                continue
            if tags and not any(tag in item['tags'] for tag in tags):
                continue
            filtered.append(item)
        
        return filtered[:limit]
    
    def generate_knowledge_report(self):
        """生成知识库统计报告"""
        try:
            sql = """
                SELECT category, COUNT(*) as count, 
                       GROUP_CONCAT(DISTINCT tags) as all_tags
                FROM knowledge_base 
                WHERE is_deleted = 0 
                GROUP BY category
                ORDER BY count DESC
            """
            results = self.chat.conn.execute(sql).fetchall()
            
            report = {
                "total_knowledge": sum(row[1] for row in results),
                "categories": {},
                "all_tags": set()
            }
            
            for category, count, tags_str in results:
                report["categories"][category] = count
                if tags_str:
                    tags = json.loads(f'[{tags_str}]')
                    for tag_list in tags:
                        if isinstance(tag_list, list):
                            report["all_tags"].update(tag_list)
            
            report["all_tags"] = list(report["all_tags"])
            
            print("\n📊 知识库统计报告")
            print("=" * 50)
            print(f"📚 总知识条目: {report['total_knowledge']}")
            print(f"📂 分类数量: {len(report['categories'])}")
            print(f"🏷️  标签数量: {len(report['all_tags'])}")
            print("\n📂 分类统计:")
            for category, count in report["categories"].items():
                print(f"   {category}: {count}条")
            
            return report
            
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            return {}
    
    def interactive_cli(self):
        """交互式CLI界面"""
        print("\n🎮 seekdb高级知识库管理器")
        print("=" * 50)
        print("📋 当前知识库统计:")
        self.generate_knowledge_report()
        
        while True:
            print("\n🎯 可用功能:")
            print("1. 🔍 高级搜索")
            print("2. 📂 按分类浏览")
            print("3. 📥 批量导入")
            print("4. 📊 生成报告")
            print("5. 🧹 清空知识库")
            print("6. ❌ 退出")
            
            try:
                choice = input("\n请选择操作 (1-6): ").strip()
                
                if choice == "1":
                    query = input("搜索词: ")
                    category = input("分类(可选): ") or None
                    tags_input = input("标签(逗号分隔,可选): ")
                    tags = [t.strip() for t in tags_input.split(",")] if tags_input else None
                    limit = int(input("结果数量(默认10): ") or "10")
                    
                    results = self.search_with_filters(query, category, tags, limit)
                    
                    if results:
                        print(f"\n🔍 找到 {len(results)} 条结果:")
                        for i, item in enumerate(results, 1):
                            print(f"\n{i}. {item['title']}")
                            print(f"   分类: {item['category']}")
                            print(f"   标签: {', '.join(item['tags'])}")
                            print(f"   内容: {item['content'][:200]}...")
                    else:
                        print("❌ 未找到匹配结果")
                
                elif choice == "2":
                    category = input("输入分类名: ")
                    self.chat.list_knowledge(category)
                
                elif choice == "3":
                    filepath = input("文件路径: ")
                    category = input("分类(默认imported): ") or "imported"
                    self.import_from_file(filepath, category)
                
                elif choice == "4":
                    self.generate_knowledge_report()
                
                elif choice == "5":
                    confirm = input("⚠️ 确定要清空知识库吗？(y/N): ")
                    if confirm.lower() == 'y':
                        self.chat.conn.execute("UPDATE knowledge_base SET is_deleted = 1")
                        self.chat.conn.commit()
                        print("✅ 知识库已清空")
                
                elif choice == "6":
                    print("👋 再见！")
                    break
                
                else:
                    print("❌ 无效选择")
                    
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        self.chat.close()


if __name__ == "__main__":
    manager = AdvancedKnowledgeManager()
    manager.interactive_cli()

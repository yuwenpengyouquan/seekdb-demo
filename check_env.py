#!/usr/bin/env python3
"""
seekdb环境检查脚本
检查seekdb是否正确安装和配置
"""

import sys
import subprocess
import os


def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低，需要3.8+，当前版本: {version.major}.{version.minor}")
        return False


def check_seekdb():
    """检查seekdb安装"""
    print("\n🔍 检查seekdb安装...")
    try:
        import seekdb
        print("✅ seekdb已安装")
        
        # 检查seekdb版本
        if hasattr(seekdb, '__version__'):
            print(f"✅ seekdb版本: {seekdb.__version__}")
        else:
            print("⚠️ 无法获取seekdb版本信息")
        
        # 测试seekdb连接
        print("\n🔍 测试seekdb连接...")
        conn = seekdb.connect(":memory:")
        conn.execute("SELECT 1")
        conn.close()
        print("✅ seekdb连接正常")
        return True
        
    except ImportError as e:
        print(f"❌ seekdb未安装: {e}")
        print("请运行: pip install seekdb")
        return False
    except Exception as e:
        print(f"❌ seekdb测试失败: {e}")
        return False


def check_dependencies():
    """检查其他依赖"""
    print("\n🔍 检查其他依赖...")
    
    dependencies = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("openai", "openai"),
        ("python_dotenv", "python-dotenv"),
    ]
    
    missing_deps = []
    
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_deps.append(package)
    
    if missing_deps:
        print(f"\n❌ 缺少依赖: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("✅ 所有依赖已安装")
        return True


def test_database_features():
    """测试seekdb核心功能"""
    print("\n🔍 测试seekdb核心功能...")
    
    try:
        import seekdb
        
        # 创建测试数据库
        conn = seekdb.connect("test_check.db")
        
        # 测试表创建
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                text_field TEXT,
                embedding VECTOR(3)
            )
        """)
        
        # 测试向量操作
        conn.execute("INSERT INTO test_table (text_field, embedding) VALUES (?, ?)", 
                    ["测试文本", [1.0, 2.0, 3.0]])
        
        # 测试查询
        result = conn.execute("SELECT * FROM test_table").fetchone()
        if result:
            print("✅ 数据库基本功能正常")
        
        # 测试向量距离计算
        try:
            conn.execute("SELECT VECTOR_DISTANCE(embedding, ?) FROM test_table", [[1.0, 2.0, 3.0]])
            print("✅ 向量距离计算正常")
        except Exception as e:
            print(f"⚠️ 向量距离测试失败: {e}")
        
        conn.close()
        
        # 清理测试文件
        try:
            os.remove("test_check.db")
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False


def main():
    """主检查流程"""
    print("🚀 seekdb环境检查工具")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_seekdb,
        check_dependencies,
        test_database_features
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 所有检查通过！seekdb环境已就绪")
        print("\n可以运行以下命令启动Demo：")
        print("  ./start_demo.sh    # 交互式启动")
        print("  python3 chat_demo.py    # 命令行版本")
        print("  python3 web_demo.py     # Web界面版本")
    else:
        print("❌ 环境检查失败，请解决上述问题后再试")
        sys.exit(1)


if __name__ == "__main__":
    main()

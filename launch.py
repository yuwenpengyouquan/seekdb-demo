#!/usr/bin/env python3
"""
seekdb AI聊天应用 - 启动器
一键启动所有功能模块
"""

import os
import sys
import subprocess
import webbrowser
import time
from threading import Thread


class SeekDBLauncher:
    """seekdb AI应用启动器"""
    
    def __init__(self):
        self.banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║    ███████╗███████╗██████╗ ██████╗  ██████╗ ████████╗      ║
    ║    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝      ║
    ║    ███████╗█████╗  ██████╔╝██████╔╝██║   ██║   ██║         ║
    ║    ╚════██║██╔══╝  ██╔═══╝ ██╔══██╗██║   ██║   ██║         ║
    ║    ███████║███████╗██║     ██║  ██║╚██████╔╝   ██║         ║
    ║    ╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝         ║
    ║                                                               ║
    ║           AI原生混合搜索数据库 · 聊天应用终极版               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
        """
    
    def check_dependencies(self):
        """检查并安装依赖"""
        print("🔍 检查依赖环境...")
        
        dependencies = [
            'flask',
            'flask-cors'
        ]
        
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                print(f"✅ {dep}")
            except ImportError:
                print(f"📦 安装 {dep}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                             capture_output=True)
    
    def run_web_app(self):
        """启动Web应用"""
        print("🌐 启动Web应用...")
        try:
            from app import app
            print("🚀 Web应用已启动")
            print("📱 访问: http://localhost:5000")
            
            # 3秒后自动打开浏览器
            def open_browser():
                time.sleep(3)
                webbrowser.open('http://localhost:5000')
            
            Thread(target=open_browser, daemon=True).start()
            app.run(debug=False, host='0.0.0.0', port=5000)
            
        except Exception as e:
            print(f"❌ Web应用启动失败: {e}")
            print("🔄 尝试启动兼容版本...")
            self.run_compatible_version()
    
    def run_compatible_version(self):
        """启动兼容版本"""
        print("🔄 启动兼容版本...")
        try:
            from chat_demo_compatible import MockSeekDBChat
            chat = MockSeekDBChat()
            
            print("🤖 启动交互式聊天...")
            session_id = "demo_session"
            
            print("\n🎮 聊天已就绪！输入 'exit' 退出")
            while True:
                user_input = input("\n👤 你: ").strip()
                if user_input.lower() in ['exit', 'quit', '退出']:
                    break
                
                response = chat.generate_response(user_input, session_id)
                print(f"🤖 AI: {response}")
                
                # 保存消息
                from chat_demo_compatible import ChatMessage
                user_msg = ChatMessage(role="user", content=user_input, session_id=session_id)
                chat.add_message(user_msg)
                
                ai_msg = ChatMessage(role="assistant", content=response, session_id=session_id)
                chat.add_message(ai_msg)
            
            chat.close()
            
        except Exception as e:
            print(f"❌ 兼容版本启动失败: {e}")
    
    def run_knowledge_manager(self):
        """启动知识库管理"""
        print("📚 启动知识库管理器...")
        try:
            from knowledge_advanced import AdvancedKnowledgeManager
            manager = AdvancedKnowledgeManager()
            manager.interactive_cli()
        except Exception as e:
            print(f"❌ 知识库管理器启动失败: {e}")
    
    def show_menu(self):
        """显示启动菜单"""
        print(self.banner)
        print("\n🎯 选择启动模式:")
        print("1. 🌐 启动Web应用（现代化界面）")
        print("2. 🤖 启动命令行聊天")
        print("3. 📚 启动知识库管理")
        print("4. 🔍 运行环境检查")
        print("5. ❌ 退出")
        
        while True:
            choice = input("\n请输入选择 (1-5): ").strip()
            
            if choice == "1":
                self.check_dependencies()
                self.run_web_app()
                break
            elif choice == "2":
                self.run_compatible_version()
                break
            elif choice == "3":
                self.run_knowledge_manager()
                break
            elif choice == "4":
                try:
                    subprocess.run([sys.executable, 'check_env.py'])
                except:
                    print("❌ 检查脚本未找到")
            elif choice == "5":
                print("👋 感谢使用seekdb AI助手！")
                break
            else:
                print("❌ 无效选择，请重试")


def main():
    """主函数"""
    launcher = SeekDBLauncher()
    launcher.show_menu()


if __name__ == "__main__":
    main()

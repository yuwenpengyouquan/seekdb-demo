#!/bin/bash

# seekdb聊天Demo启动脚本
# 陆枫 2026-02-27

echo "🚀 seekdb AI聊天Demo启动脚本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查并安装依赖
echo "📦 检查依赖..."
if [ -f "requirements.txt" ]; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
else
    echo "❌ 未找到requirements.txt文件"
    exit 1
fi

# 检查环境
echo "🔍 检查seekdb环境..."
python3 check_env.py

if [ $? -ne 0 ]; then
    echo "⚠️  seekdb环境未就绪，使用兼容版本"
    USE_COMPATIBLE=true
else
    echo "✅ seekdb环境就绪"
    USE_COMPATIBLE=false
fi

# 启动选项
echo ""
echo "请选择启动模式:"
echo "1. 命令行聊天Demo"
echo "2. Web界面聊天Demo"
echo "3. 知识库管理"
echo "4. 环境检查"
echo "5. 退出"
read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        if [ "$USE_COMPATIBLE" = true ]; then
            echo "🤖 启动兼容版命令行聊天Demo..."
            python3 chat_demo_compatible.py
        else
            echo "🤖 启动seekdb命令行聊天Demo..."
            python3 chat_demo.py
        fi
        ;;
    2)
        echo "🌐 启动Web界面聊天Demo..."
        echo "启动后请访问: http://localhost:5000"
        python3 web_demo.py
        ;;
    3)
        echo "📚 启动知识库管理工具..."
        python3 knowledge_manager.py interactive
        ;;
    4)
        echo "🔍 运行环境检查..."
        python3 check_env.py
        ;;
    5)
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo "❌ 无效选择，退出程序"
        exit 1
        ;;
esac
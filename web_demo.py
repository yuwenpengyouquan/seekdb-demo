#!/usr/bin/env python3
"""
seekdb聊天Demo的Web界面
基于Flask的简单聊天界面
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import uuid
from chat_demo_compatible import MockSeekDBChat, ChatMessage

app = Flask(__name__)
CORS(app)

# 初始化seekdb聊天系统
chat_system = MockSeekDBChat()

# HTML模板
CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>seekdb AI聊天Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 800px;
            height: 80vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.8;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }
        
        .message.user {
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
        }
        
        .message.user .message-avatar {
            background: #667eea;
        }
        
        .message.assistant .message-avatar {
            background: #764ba2;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #667eea;
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            color: #333;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }
        
        .send-button:hover:not(:disabled) {
            transform: translateY(-2px);
        }
        
        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px 20px;
            color: #666;
            font-style: italic;
        }
        
        .knowledge-info {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-size: 12px;
            color: #1976d2;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 seekdb AI助手</h1>
            <p>基于seekdb混合搜索数据库的智能对话</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message assistant">
                <div class="message-avatar">AI</div>
                <div class="message-content">
                    你好！我是基于seekdb AI原生混合搜索数据库的智能助手。我可以回答关于seekdb的问题，也可以进行日常对话。有什么我可以帮你的吗？
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            AI正在思考中...
        </div>
        
        <div class="chat-input-container">
            <input type="text" class="chat-input" id="chatInput" placeholder="输入你的问题..." maxlength="500">
            <button class="send-button" id="sendButton" onclick="sendMessage()">发送</button>
        </div>
    </div>

    <script>
        let sessionId = localStorage.getItem('sessionId') || generateSessionId();
        localStorage.setItem('sessionId', sessionId);

        function generateSessionId() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }

        function addMessage(role, content) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            messageDiv.innerHTML = `
                <div class="message-avatar">${role === 'user' ? '你' : 'AI'}</div>
                <div class="message-content">${content}</div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // 添加用户消息
            addMessage('user', message);
            input.value = '';
            
            // 显示正在输入
            document.getElementById('typingIndicator').style.display = 'block';
            
            // 发送到服务器
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('typingIndicator').style.display = 'none';
                
                if (data.success) {
                    addMessage('assistant', data.response);
                } else {
                    addMessage('assistant', '抱歉，我遇到了一些问题，请稍后再试。');
                }
            })
            .catch(error => {
                document.getElementById('typingIndicator').style.display = 'none';
                console.error('Error:', error);
                addMessage('assistant', '网络连接出现问题，请检查网络后重试。');
            });
        }

        // 监听回车键
        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // 页面加载时加载历史消息
        window.addEventListener('load', function() {
            fetch(`/history/${sessionId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.messages.length > 1) {
                        const messagesContainer = document.getElementById('chatMessages');
                        messagesContainer.innerHTML = '';
                        
                        data.messages.forEach(msg => {
                            addMessage(msg.role, msg.content);
                        });
                    }
                });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页面"""
    return render_template_string(CHAT_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'success': False, 'error': '消息不能为空'})
        
        # 保存用户消息
        user_msg = ChatMessage(role='user', content=user_message, session_id=session_id)
        chat_system.add_message(user_msg)
        
        # 生成AI回复
        ai_response = chat_system.generate_response(user_message, session_id)
        
        # 保存AI回复
        ai_msg = ChatMessage(role='assistant', content=ai_response, session_id=session_id)
        chat_system.add_message(ai_msg)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"聊天接口错误: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/history/<session_id>')
def get_history(session_id):
    """获取聊天历史"""
    try:
        messages = chat_system.get_chat_history(session_id)
        return jsonify({
            'success': True,
            'messages': [{
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
            } for msg in messages]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/knowledge', methods=['POST'])
def add_knowledge():
    """添加知识（API接口）"""
    try:
        data = request.json
        chat_system.add_knowledge(
            title=data.get('title', ''),
            content=data.get('content', ''),
            category=data.get('category', 'general'),
            tags=data.get('tags', [])
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # 初始化示例知识
    print("🚀 正在初始化seekdb聊天系统...")
    
    # 添加一些基础知识点
    chat_system.add_knowledge(
        "seekdb是什么？",
        "seekdb是OceanBase推出的AI原生混合搜索数据库，在一个数据库中融合向量、文本、结构化与半结构化数据能力，并通过内置AI Functions支持多模混合搜索与智能推理。",
        "产品介绍"
    )
    
    chat_system.add_knowledge(
        "seekdb的主要特性",
        """seekdb具有以下核心特性：
        1. 混合搜索：支持向量搜索、全文搜索、标量过滤的混合查询
        2. AI内置：支持AI_EMBED、AI_COMPLETE、AI_RERANK等AI函数
        3. MySQL兼容：完全兼容MySQL协议和语法
        4. 多模数据：支持向量、文本、JSON、GIS等多种数据类型
        5. 轻量部署：支持嵌入式和服务器两种部署模式""",
        "产品特性"
    )
    
    chat_system.add_knowledge(
        "如何安装seekdb？",
        """seekdb支持多种安装方式：
        1. Python安装：pip install seekdb
        2. 嵌入式模式：直接import seekdb即可使用
        3. 服务器模式：下载seekdb server版本""",
        "使用指南"
    )
    
    print("✅ 示例知识已加载")
    print("🌐 Web服务器启动: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

#!/usr/bin/env python3
"""
seekdb AI聊天应用 - 终极版Web界面
满分级别的现代化设计，支持暗色/亮色主题
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import uuid
import json
import os
from chat_demo_compatible import MockSeekDBChat, ChatMessage

app = Flask(__name__)
CORS(app)

# 初始化seekdb聊天系统
chat_system = MockSeekDBChat()

# 现代化的HTML模板
ULTIMATE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 seekdb AI助手 - 终极版</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f1419;
            --bg-secondary: #1a1d29;
            --bg-tertiary: #252837;
            --text-primary: #ffffff;
            --text-secondary: #a1a1aa;
            --accent: #6366f1;
            --accent-hover: #818cf8;
            --border: #374151;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --card-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            --glow: 0 0 20px rgba(99, 102, 241, 0.3);
        }

        [data-theme="light"] {
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #e2e8f0;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border: #cbd5e1;
            --card-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .app-container {
            display: flex;
            height: 100vh;
            backdrop-filter: blur(20px);
        }

        .sidebar {
            width: 280px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }

        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid var(--border);
            background: var(--gradient);
            color: white;
            text-align: center;
        }

        .logo {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .tagline {
            font-size: 12px;
            opacity: 0.8;
        }

        .session-list {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }

        .session-item {
            padding: 12px 16px;
            margin: 4px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }

        .session-item:hover {
            background: var(--bg-tertiary);
            transform: translateX(2px);
        }

        .session-item.active {
            background: var(--accent);
            color: white;
            box-shadow: var(--glow);
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: var(--bg-secondary);
            padding: 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-title {
            font-size: 20px;
            font-weight: 600;
        }

        .header-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .theme-toggle {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 20px;
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .theme-toggle:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: var(--bg-primary);
        }

        .message {
            display: flex;
            margin-bottom: 20px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            margin-right: 12px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: var(--gradient);
            color: white;
        }

        .message.assistant .message-avatar {
            background: var(--bg-tertiary);
            color: var(--accent);
        }

        .message-content {
            max-width: 70%;
            padding: 16px 20px;
            border-radius: 16px;
            word-wrap: break-word;
            line-height: 1.5;
        }

        .message.user .message-content {
            background: var(--gradient);
            color: white;
            box-shadow: var(--glow);
        }

        .message.assistant .message-content {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            box-shadow: var(--card-shadow);
        }

        .input-area {
            background: var(--bg-secondary);
            padding: 20px;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 12px;
            align-items: end;
        }

        .input-container {
            flex: 1;
            position: relative;
        }

        .chat-input {
            width: 100%;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 16px 20px;
            font-size: 16px;
            color: var(--text-primary);
            resize: none;
            max-height: 120px;
            transition: all 0.2s ease;
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .send-button {
            background: var(--gradient);
            color: white;
            border: none;
            padding: 16px 24px;
            border-radius: 24px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }

        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: var(--glow);
        }

        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .typing-indicator {
            display: none;
            padding: 20px;
            color: var(--text-secondary);
            font-style: italic;
            animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        .welcome-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            padding: 40px;
        }

        .welcome-icon {
            font-size: 80px;
            margin-bottom: 20px;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .welcome-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .welcome-subtitle {
            font-size: 18px;
            color: var(--text-secondary);
            margin-bottom: 30px;
        }

        .feature-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
            width: 100%;
            max-width: 600px;
        }

        .feature-card {
            background: var(--bg-secondary);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid var(--border);
            text-align: center;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--card-shadow);
            border-color: var(--accent);
        }

        .feature-icon {
            font-size: 32px;
            margin-bottom: 12px;
            color: var(--accent);
        }

        .feature-title {
            font-weight: 600;
            margin-bottom: 8px;
        }

        .feature-desc {
            font-size: 14px;
            color: var(--text-secondary);
        }

        .sidebar-toggle {
            display: none;
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 24px;
            cursor: pointer;
            margin-right: 16px;
        }

        .new-chat-btn {
            width: 100%;
            background: var(--accent);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            margin: 10px;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .new-chat-btn:hover {
            background: var(--accent-hover);
            transform: translateY(-1px);
        }

        @media (max-width: 768px) {
            .sidebar {
                position: fixed;
                left: -280px;
                top: 0;
                height: 100vh;
                z-index: 1000;
                transition: left 0.3s ease;
            }

            .sidebar.open {
                left: 0;
            }

            .sidebar-toggle {
                display: block;
            }

            .header {
                padding: 16px;
            }
        }
    </style>
</head>
<body data-theme="dark">
    <div class="app-container">
        <!-- 侧边栏 -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <div class="logo">🤖 seekdb</div>
                <div class="tagline">AI原生聊天助手</div>
            </div>
            <button class="new-chat-btn" onclick="createNewSession()">
                <i class="fas fa-plus"></i> 新对话
            </button>
            <div class="session-list" id="sessionList">
                <!-- 会话列表将动态生成 -->
            </div>
        </div>

        <!-- 主内容区 -->
        <div class="main-content">
            <div class="header">
                <div style="display: flex; align-items: center;">
                    <button class="sidebar-toggle" onclick="toggleSidebar()">
                        <i class="fas fa-bars"></i>
                    </button>
                    <div class="header-title" id="currentSessionTitle">新的对话</div>
                </div>
                <div class="header-controls">
                    <button class="theme-toggle" onclick="toggleTheme()" title="切换主题">
                        <i class="fas fa-sun" id="themeIcon"></i>
                    </button>
                </div>
            </div>

            <div class="chat-container">
                <div class="messages-area" id="messagesArea">
                    <div class="welcome-screen" id="welcomeScreen">
                        <div class="welcome-icon">🚀</div>
                        <div class="welcome-title">欢迎使用seekdb AI助手</div>
                        <div class="welcome-subtitle">基于AI原生混合搜索数据库的智能对话系统</div>
                        
                        <div class="feature-cards">
                            <div class="feature-card">
                                <div class="feature-icon">🧠</div>
                                <div class="feature-title">智能对话</div>
                                <div class="feature-desc">上下文感知，自然语言理解</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">🔍</div>
                                <div class="feature-title">混合搜索</div>
                                <div class="feature-desc">向量+全文，精准匹配</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">📚</div>
                                <div class="feature-title">知识管理</div>
                                <div class="feature-desc">动态知识库，实时更新</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="typing-indicator" id="typingIndicator">
                    <i class="fas fa-robot"></i> AI正在思考中...
                </div>

                <div class="input-area">
                    <div class="input-container">
                        <textarea 
                            class="chat-input" 
                            id="chatInput" 
                            placeholder="输入你的问题..." 
                            maxlength="1000"
                            rows="1"
                        ></textarea>
                    </div>
                    <button class="send-button" id="sendButton" onclick="sendMessage()">
                        <i class="fas fa-paper-plane"></i>
                        发送
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        let sessions = [];

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadSessions();
            createNewSession();
            setupThemeToggle();
            setupTextareaAutoResize();
        });

        function setupThemeToggle() {
            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);
        }

        function toggleTheme() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        }

        function setTheme(theme) {
            document.body.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            const icon = document.getElementById('themeIcon');
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }

        function setupTextareaAutoResize() {
            const textarea = document.getElementById('chatInput');
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
        }

        function createNewSession() {
            const sessionId = 'session_' + Date.now();
            const session = {
                id: sessionId,
                title: '新的对话',
                timestamp: new Date().toISOString()
            };
            sessions.unshift(session);
            saveSessions();
            loadSessions();
            switchSession(sessionId);
        }

        function switchSession(sessionId) {
            currentSessionId = sessionId;
            const session = sessions.find(s => s.id === sessionId);
            if (session) {
                document.getElementById('currentSessionTitle').textContent = session.title;
                loadMessages();
                updateSessionList();
            }
        }

        function loadSessions() {
            const saved = localStorage.getItem('chat_sessions');
            if (saved) {
                sessions = JSON.parse(saved);
            }
            updateSessionList();
        }

        function saveSessions() {
            localStorage.setItem('chat_sessions', JSON.stringify(sessions));
        }

        function updateSessionList() {
            const list = document.getElementById('sessionList');
            list.innerHTML = '';
            sessions.forEach(session => {
                const div = document.createElement('div');
                div.className = `session-item ${session.id === currentSessionId ? 'active' : ''}`;
                div.onclick = () => switchSession(session.id);
                div.innerHTML = `
                    <div style="font-weight: 500; margin-bottom: 4px;">${session.title}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">
                        ${new Date(session.timestamp).toLocaleDateString()}
                    </div>
                `;
                list.appendChild(div);
            });
        }

        function loadMessages() {
            if (!currentSessionId) return;
            
            fetch(`/history/${currentSessionId}`)
                .then(response => response.json())
                .then(data => {
                    const area = document.getElementById('messagesArea');
                    const welcome = document.getElementById('welcomeScreen');
                    
                    if (data.success && data.messages.length > 0) {
                        welcome.style.display = 'none';
                        area.innerHTML = '';
                        data.messages.forEach(msg => addMessageToUI(msg.role, msg.content, false));
                    } else {
                        welcome.style.display = 'flex';
                    }
                });
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message || !currentSessionId) return;
            
            input.value = '';
            input.style.height = 'auto';
            
            document.getElementById('welcomeScreen').style.display = 'none';
            addMessageToUI('user', message, true);
            
            showTypingIndicator();
            
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: currentSessionId
                })
            })
            .then(response => response.json())
            .then(data => {
                hideTypingIndicator();
                if (data.success) {
                    addMessageToUI('assistant', data.response, true);
                    
                    // 更新会话标题
                    const session = sessions.find(s => s.id === currentSessionId);
                    if (session && session.title === '新的对话') {
                        session.title = message.substring(0, 20) + (message.length > 20 ? '...' : '');
                        saveSessions();
                        updateSessionList();
                    }
                }
            })
            .catch(error => {
                hideTypingIndicator();
                addMessageToUI('assistant', '抱歉，我遇到了一些问题，请稍后再试。', true);
            });
        }

        function addMessageToUI(role, content, animate = false) {
            const area = document.getElementById('messagesArea');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            if (animate) messageDiv.style.animation = 'fadeIn 0.3s ease';
            
            const avatar = role === 'user' ? '👤' : '🤖';
            
            messageDiv.innerHTML = `
                <div class="message-avatar">${avatar}</div>
                <div class="message-content">${content}</div>
            `;
            
            area.appendChild(messageDiv);
            area.scrollTop = area.scrollHeight;
        }

        function showTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'block';
            document.getElementById('messagesArea').scrollTop = document.getElementById('messagesArea').scrollHeight;
        }

        function hideTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'none';
        }

        // 键盘事件
        document.getElementById('chatInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // 点击外部关闭侧边栏（移动设备）
        document.addEventListener('click', function(e) {
            const sidebar = document.getElementById('sidebar');
            const toggle = document.querySelector('.sidebar-toggle');
            
            if (window.innerWidth <= 768 && 
                !sidebar.contains(e.target) && 
                !toggle.contains(e.target) && 
                sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页面"""
    return render_template_string(ULTIMATE_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message or not session_id:
            return jsonify({'success': False, 'error': '参数不完整'})
        
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

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """获取所有会话"""
    return jsonify({'success': True, 'sessions': []})

if __name__ == '__main__':
    print("🚀 启动seekdb AI助手 - 终极版")
    print("🌐 访问 http://localhost:5000")
    print("🎨 支持暗色/亮色主题切换")
    print("📱 移动端响应式设计")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

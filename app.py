from flask import Flask, request, jsonify, render_template_string
from google import genai
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# === API KEY ===
API_KEY = "AIzaSyD1tV5Zav3lH3_doWRauEnQ2cQmleR8c5k"
client = genai.Client(api_key=API_KEY)

# === HTML UI ===
html = """
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🤖 AI Adrian Chat</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #f1f5f9;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      position: relative;
      overflow: hidden;
    }
    
    body::before {
      content: '';
      position: absolute;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
      background-size: 50px 50px;
      animation: moveBackground 20s linear infinite;
      z-index: 0;
    }
    
    @keyframes moveBackground {
      0% { transform: translate(0, 0); }
      100% { transform: translate(50px, 50px); }
    }
    
    .container {
      width: 100%;
      max-width: 700px;
      background: rgba(30, 41, 59, 0.95);
      backdrop-filter: blur(10px);
      border-radius: 24px;
      padding: 30px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      display: flex;
      flex-direction: column;
      height: 90vh;
      max-height: 800px;
      position: relative;
      z-index: 1;
      border: 1px solid rgba(255,255,255,0.1);
      animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .header {
      text-align: center;
      margin-bottom: 20px;
      padding-bottom: 20px;
      border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    
    .header h2 {
      font-size: 28px;
      font-weight: 700;
      background: linear-gradient(90deg, #60a5fa, #a78bfa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 5px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }
    
    .header p {
      color: #94a3b8;
      font-size: 14px;
    }
    
    .chat-box {
      overflow-y: auto;
      flex-grow: 1;
      margin-bottom: 20px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .chat-box::-webkit-scrollbar {
      width: 6px;
    }
    
    .chat-box::-webkit-scrollbar-track {
      background: rgba(255,255,255,0.05);
      border-radius: 10px;
    }
    
    .chat-box::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.2);
      border-radius: 10px;
    }
    
    .chat-box::-webkit-scrollbar-thumb:hover {
      background: rgba(255,255,255,0.3);
    }
    
    .msg {
      padding: 14px 18px;
      border-radius: 16px;
      max-width: 80%;
      line-height: 1.5;
      word-wrap: break-word;
      white-space: pre-wrap;
      animation: slideIn 0.3s ease-out;
      position: relative;
    }
    
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .user {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      align-self: flex-end;
      border-bottom-right-radius: 4px;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .ai {
      background: linear-gradient(135deg, #434343 0%, #000000 100%);
      color: #e2e8f0;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .input-area {
      background: rgba(15, 23, 42, 0.6);
      border-radius: 16px;
      padding: 12px;
      border: 2px solid rgba(255,255,255,0.1);
      transition: all 0.3s ease;
    }
    
    .input-area:focus-within {
      border-color: rgba(102, 126, 234, 0.5);
      box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
    }
    
    form {
      display: flex;
      gap: 10px;
      align-items: center;
    }
    
    textarea {
      flex-grow: 1;
      resize: none;
      padding: 12px 16px;
      border: none;
      border-radius: 12px;
      font-size: 15px;
      background: rgba(255,255,255,0.05);
      color: #f1f5f9;
      outline: none;
      font-family: inherit;
      transition: background 0.3s ease;
    }
    
    textarea:focus {
      background: rgba(255,255,255,0.08);
    }
    
    textarea::placeholder {
      color: #64748b;
    }
    
    button {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: white;
      border: none;
      border-radius: 12px;
      padding: 12px 24px;
      cursor: pointer;
      font-weight: 600;
      font-size: 15px;
      transition: all 0.3s ease;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
      white-space: nowrap;
    }
    
    button:hover {
      background: linear-gradient(135deg, #059669 0%, #047857 100%);
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
    }
    
    button:active {
      transform: translateY(0);
    }
    
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #64748b;
      text-align: center;
    }
    
    .empty-state-icon {
      font-size: 64px;
      margin-bottom: 16px;
      opacity: 0.5;
    }
    
    .empty-state-text {
      font-size: 18px;
      margin-bottom: 8px;
    }
    
    .empty-state-subtext {
      font-size: 14px;
      opacity: 0.7;
    }
    
    .thinking {
      padding: 14px 18px;
      border-radius: 16px;
      max-width: 80%;
      line-height: 1.5;
      background: linear-gradient(135deg, #434343 0%, #000000 100%);
      color: #e2e8f0;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      display: flex;
      align-items: center;
      gap: 8px;
      animation: slideIn 0.3s ease-out;
    }
    
    .thinking-dots {
      display: flex;
      gap: 4px;
    }
    
    .thinking-dots span {
      width: 8px;
      height: 8px;
      background: #60a5fa;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out;
    }
    
    .thinking-dots span:nth-child(1) {
      animation-delay: -0.32s;
    }
    
    .thinking-dots span:nth-child(2) {
      animation-delay: -0.16s;
    }
    
    @keyframes bounce {
      0%, 80%, 100% {
        transform: scale(0);
        opacity: 0.5;
      }
      40% {
        transform: scale(1);
        opacity: 1;
      }
    }
    
    @media (max-width: 768px) {
      .container {
        padding: 20px;
        height: 95vh;
      }
      
      .header h2 {
        font-size: 24px;
      }
      
      .msg {
        max-width: 85%;
      }
      
      button {
        padding: 12px 16px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>
        <span>🤖</span>
        <span>AI by Adrian</span>
      </h2>
      <p>Asisten AI yang siap membantu Anda</p>
    </div>
    
    <div class="chat-box" id="chat">
      <div class="empty-state">
        <div class="empty-state-icon">💬</div>
        <div class="empty-state-text">Mulai percakapan</div>
        <div class="empty-state-subtext">Ketik pertanyaan Anda di bawah untuk memulai</div>
      </div>
    </div>
    
    <div class="input-area">
      <form id="form">
        <textarea id="task" placeholder="Tulis pertanyaan kamu..." rows="1"></textarea>
        <button type="submit">Kirim</button>
      </form>
    </div>
  </div>

  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('form');
    const input = document.getElementById('task');

    function addMessage(sender, text) {
      // Remove empty state if exists
      const emptyState = chat.querySelector('.empty-state');
      if (emptyState) {
        emptyState.remove();
      }
      
      const div = document.createElement('div');
      div.className = 'msg ' + sender;
      div.innerText = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }
    
    function showThinking() {
      const thinkingDiv = document.createElement('div');
      thinkingDiv.className = 'thinking';
      thinkingDiv.id = 'thinking-indicator';
      thinkingDiv.innerHTML = `
        <span>AI sedang berpikir</span>
        <div class="thinking-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      `;
      chat.appendChild(thinkingDiv);
      chat.scrollTop = chat.scrollHeight;
    }
    
    function hideThinking() {
      const thinkingDiv = document.getElementById('thinking-indicator');
      if (thinkingDiv) {
        thinkingDiv.remove();
      }
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const question = input.value.trim();
      if (!question) return;
      addMessage('user', question);
      input.value = '';
      
      // Show thinking indicator
      showThinking();
      
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
      });
      const data = await res.json();
      
      // Hide thinking indicator
      hideThinking();
      
      if (data.answer) {
        addMessage('ai', data.answer);
        localStorage.setItem('chatHistory', chat.innerHTML);
      } else {
        addMessage('ai', '⚠️ Terjadi kesalahan. Coba lagi.');
      }
    });

    window.onload = () => {
      const saved = localStorage.getItem('chatHistory');
      if (saved) chat.innerHTML = saved;
      chat.scrollTop = chat.scrollHeight;
    };
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    try:
        # Waktu lokal WIB (UTC+7)
        wib = timezone(timedelta(hours=7))
        now = datetime.now(wib).strftime("%A, %d %B %Y %H:%M:%S WIB")

        prompt = (
            f"Sekarang waktu lokal Indonesia (WIB): {now}. "
            f"Gunakan informasi ini saat menjawab. Pertanyaan: {question}"
        )

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )

        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"answer": f"❌ Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
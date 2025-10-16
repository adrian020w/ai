from flask import Flask, request, jsonify, render_template_string
from google import genai
from datetime import datetime, timedelta, timezone

# === Konfigurasi Flask ===
app = Flask(__name__)

# === API KEY ===
API_KEY = "AIzaSyD1tV5Zav3lH3_doWRauEnQ2cQmleR8c5k"
client = genai.Client(api_key=API_KEY)

# === HTML Frontend ===
html = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🤖 AI by Adrian</title>
  <style>
    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #f1f5f9;
      font-family: Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0;
      padding: 0;
    }
    .container {
      background: rgba(30, 41, 59, 0.95);
      backdrop-filter: blur(10px);
      padding: 20px;
      border-radius: 16px;
      width: 90%;
      max-width: 700px;
      height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    }
    h2 {
      text-align: center;
      margin-bottom: 10px;
      background: linear-gradient(90deg, #60a5fa, #a78bfa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .chat-box {
      flex-grow: 1;
      overflow-y: auto;
      margin-bottom: 10px;
      padding-right: 8px;
    }
    .msg {
      margin: 6px 0;
      padding: 10px 14px;
      border-radius: 12px;
      max-width: 80%;
      word-wrap: break-word;
      white-space: pre-wrap;
      animation: fadeIn 0.3s ease;
    }
    .user {
      background: #2563eb;
      color: white;
      align-self: flex-end;
    }
    .ai {
      background: #334155;
      color: #e2e8f0;
      align-self: flex-start;
    }
    form {
      display: flex;
    }
    textarea {
      flex-grow: 1;
      border: none;
      border-radius: 10px;
      padding: 10px;
      font-size: 16px;
      resize: none;
    }
    button {
      background: #10b981;
      border: none;
      color: white;
      font-weight: bold;
      border-radius: 10px;
      padding: 10px 18px;
      margin-left: 8px;
      cursor: pointer;
    }
    button:hover {
      background: #059669;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>🤖 AI by Adrian</h2>
    <div id="chat" class="chat-box"></div>
    <form id="form">
      <textarea id="task" placeholder="Tulis pertanyaan kamu..." rows="1"></textarea>
      <button type="submit">Kirim</button>
    </form>
  </div>

  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('form');
    const input = document.getElementById('task');

    function addMessage(sender, text) {
      const div = document.createElement('div');
      div.className = 'msg ' + sender;
      div.innerText = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const question = input.value.trim();
      if (!question) return;
      addMessage('user', question);
      input.value = '';
      addMessage('ai', '⏳ Sedang berpikir...');
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
      });
      const data = await res.json();
      chat.lastChild.remove(); // hapus "Sedang berpikir..."
      addMessage('ai', data.answer || '⚠️ Terjadi kesalahan.');
    });
  </script>
</body>
</html>"""

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

        prompt = f"Sekarang waktu lokal Indonesia (WIB): {now}. Jawablah pertanyaan ini dengan konteks waktu tersebut: {question}"

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )

        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"answer": f"❌ Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

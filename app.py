from flask import Flask, request, jsonify, render_template_string
import requests
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

API_KEY = "AIzaSyD1tV5Zav3lH3_doWRauEnQ2cQmleR8c5k"
AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# === Orion AI News (dengan desain & animasi baru) ===
html = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🌌 Orion AI by adrian</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    body {
      margin: 0;
      font-family: 'Poppins', sans-serif;
      background: radial-gradient(circle at 20% 20%, #0f172a, #1e293b 60%, #020617);
      color: #e2e8f0;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .stars {
      position: absolute;
      width: 2px;
      height: 2px;
      background: white;
      animation: twinkle 4s infinite ease-in-out;
      border-radius: 50%;
      opacity: 0.7;
    }

    @keyframes twinkle {
      0%, 100% { opacity: 0.2; transform: scale(1); }
      50% { opacity: 1; transform: scale(1.6); }
    }

    .container {
      position: relative;
      z-index: 2;
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid rgba(100, 116, 139, 0.3);
      border-radius: 20px;
      width: 90%;
      max-width: 700px;
      height: 85vh;
      display: flex;
      flex-direction: column;
      padding: 20px;
      box-shadow: 0 0 25px rgba(59, 130, 246, 0.4);
      backdrop-filter: blur(15px);
    }

    h2 {
      text-align: center;
      font-size: 2rem;
      margin-bottom: 6px;
      background: linear-gradient(90deg, #38bdf8, #a855f7, #6366f1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: pulse 3s infinite alternate;
    }

    @keyframes pulse {
      0% { text-shadow: 0 0 8px rgba(59,130,246,0.3); }
      100% { text-shadow: 0 0 20px rgba(168,85,247,0.6); }
    }

    .subtitle {
      text-align: center;
      color: #94a3b8;
      font-size: 0.9rem;
      margin-bottom: 15px;
    }

    .chat-box {
      flex-grow: 1;
      overflow-y: auto;
      background: rgba(30, 41, 59, 0.6);
      border-radius: 12px;
      padding: 12px;
      scrollbar-width: thin;
      scroll-behavior: smooth;
    }

    .msg {
      margin: 8px 0;
      padding: 10px 14px;
      border-radius: 12px;
      max-width: 80%;
      white-space: pre-wrap;
      animation: fadeIn 0.4s ease;
    }

    .user {
      background: linear-gradient(135deg, #2563eb, #3b82f6);
      color: white;
      align-self: flex-end;
    }

    .ai {
      background: rgba(148, 163, 184, 0.15);
      border: 1px solid rgba(148, 163, 184, 0.2);
      color: #e2e8f0;
      align-self: flex-start;
    }

    form {
      display: flex;
      margin-top: 10px;
    }

    textarea {
      flex-grow: 1;
      border: none;
      border-radius: 10px;
      padding: 10px;
      font-size: 15px;
      resize: none;
      outline: none;
      background: rgba(51, 65, 85, 0.5);
      color: #f1f5f9;
    }

    button {
      background: linear-gradient(90deg, #06b6d4, #3b82f6);
      border: none;
      color: white;
      font-weight: bold;
      border-radius: 10px;
      padding: 10px 18px;
      margin-left: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    button:hover {
      background: linear-gradient(90deg, #0ea5e9, #6366f1);
      transform: scale(1.05);
    }

    .clear-btn {
      position: absolute;
      top: 10px;
      right: 15px;
      background: transparent;
      border: none;
      color: #94a3b8;
      cursor: pointer;
      font-size: 14px;
    }

    .clear-btn:hover { color: #f87171; }

    .loader {
      display: flex;
      gap: 6px;
      margin: 6px 0;
      padding-left: 6px;
    }

    .dot {
      width: 10px;
      height: 10px;
      background: #60a5fa;
      border-radius: 50%;
      animation: bounce 0.8s infinite alternate;
    }

    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes bounce {
      from { transform: translateY(0); opacity: 0.5; }
      to { transform: translateY(-8px); opacity: 1; }
    }

    @keyframes fadeIn {
      from {opacity: 0; transform: translateY(10px);}
      to {opacity: 1; transform: translateY(0);}
    }
  </style>
</head>
<body>
  <div class="stars" style="top:10%; left:30%; animation-delay:0.3s;"></div>
  <div class="stars" style="top:50%; left:70%; animation-delay:1s;"></div>
  <div class="stars" style="top:80%; left:40%; animation-delay:2s;"></div>

  <div class="container">
    <button class="clear-btn" id="clearHistory">🧹 Bersihkan</button>
    <h2>🌌 Orion AI by adrian</h2>
    <div class="subtitle">AI cerdas dengan berita terkini dari seluruh dunia 🌍</div>

    <div id="chat" class="chat-box"></div>

    <form id="form">
      <textarea id="task" placeholder="Ketik pertanyaan atau topik berita..." rows="1"></textarea>
      <button type="submit">Kirim</button>
    </form>
  </div>

  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('form');
    const input = document.getElementById('task');
    const clearBtn = document.getElementById('clearHistory');

    function addMessage(sender, text, save = true) {
      const div = document.createElement('div');
      div.className = 'msg ' + sender;
      div.innerText = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
      if (save) {
        let history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
        history.push({ sender, text });
        localStorage.setItem('chatHistory', JSON.stringify(history));
      }
    }

    function showLoader() {
      const loader = document.createElement('div');
      loader.className = 'loader ai';
      loader.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
      chat.appendChild(loader);
      chat.scrollTop = chat.scrollHeight;
      return loader;
    }

    window.onload = () => {
      let history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
      for (const msg of history) addMessage(msg.sender, msg.text, false);
    };

    clearBtn.onclick = () => {
      localStorage.removeItem('chatHistory');
      chat.innerHTML = '';
      addMessage('ai', '🧹 Riwayat percakapan dibersihkan.', true);
    };

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const question = input.value.trim();
      if (!question) return;
      addMessage('user', question);
      input.value = '';
      const loader = showLoader();
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
      });
      const data = await res.json();
      loader.remove();
      addMessage('ai', data.answer || '⚠️ Terjadi kesalahan.');
    });
  </script>
</body>
</html>"""

# === Ambil berita terkini dari Google News ===
def get_latest_news(query):
    try:
        url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=id&gl=ID&ceid=ID:id"
        r = requests.get(url)
        if r.status_code != 200:
            return "Gagal mengambil berita terbaru."
        import re
        items = re.findall(r"<title>(.*?)</title><link>(.*?)</link>", r.text)
        if len(items) > 1:
            news_list = []
            for title, link in items[1:5]:
                news_list.append(f"📰 {title}\n🔗 {link}")
            return "\n\n".join(news_list)
        else:
            return "Tidak ada berita terbaru ditemukan."
    except Exception as e:
        return f"❌ Gagal ambil berita: {str(e)}"

@app.route("/")
def home():
    return render_template_string(html)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    try:
        wib = timezone(timedelta(hours=7))
        now = datetime.now(wib)
        waktu_str = now.strftime("%A, %d %B %Y %H:%M:%S WIB")

        # Jika user minta berita
        if "berita" in question.lower() or "news" in question.lower():
            topic = question.replace("berita", "").replace("terbaru", "").strip()
            news_data = get_latest_news(topic if topic else "Indonesia")
            return jsonify({"answer": f"📅 {waktu_str}\n\n{news_data}"})

        # Tanya ke AI Gemini
        payload = {"contents": [{"parts": [{"text": f"Sekarang {waktu_str}. {question}"}]}]}
        response = requests.post(AI_URL, json=payload)
        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"❌ Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

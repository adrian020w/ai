from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

# ==========================================
# ⚠️ KONFIGURASI API KEY (GEMINI 2.0 FLASH)
# ==========================================
API_KEY = "AIzaSyCH1myR7PH_mJM_Xo94otL_31eYUoXkh0s"
AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# --- SYSTEM INSTRUCTION ---
SYSTEM_PROMPT = """
Kamu adalah Orion AI.
PENTING:
1. Kalau memberikan kodingan (Python, HTML, CSS, JS, dll), WAJIB apit dengan ```nama_bahasa ... ```.
2. Jangan campur kode dengan teks biasa dalam satu paragraf. Pisahkan blok kodenya.
"""

# ==========================================
# 🎨 FRONTEND (HOVER SIDEBAR + MODERN UI)
# ==========================================
html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌌 Orion AI by Adrian</title>

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

<style>
/* --- RESET & GLOBAL --- */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Poppins', sans-serif;
  height: 100vh; overflow: hidden; 
  background: #0f172a; 
  color: #e2e8f0;
  display: flex;
}

/* --- SIDEBAR (HOVER EFFECT) --- */
.sidebar {
  position: fixed; /* Mengambang di kiri */
  left: 0; top: 0; bottom: 0;
  width: 12px; /* Default: hanya garis tipis pemicu */
  background: linear-gradient(to bottom, #3b82f6, #a855f7); /* Warna garis indikator */
  z-index: 1000; /* Di atas chat */
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s;
  overflow: hidden; /* Sembunyikan isi saat tertutup */
  box-shadow: 2px 0 15px rgba(59, 130, 246, 0.5); /* Efek glow */
  
  /* Glassmorphism saat terbuka */
  backdrop-filter: blur(0px);
}

/* KETIKA KURSOR DIARAHKAN (HOVER) */
.sidebar:hover {
  width: 300px; /* Melebar */
  background: rgba(15, 23, 42, 0.95); /* Jadi gelap transparan */
  backdrop-filter: blur(10px);
  box-shadow: 10px 0 30px rgba(0,0,0,0.5);
  border-right: 1px solid #334155;
}

/* Konten Sidebar (Agar tidak berantakan saat animasi) */
.sidebar-content {
  width: 300px; /* Lebar tetap konten */
  padding: 20px;
  display: flex; flex-direction: column; height: 100%;
  opacity: 0; /* Hilang saat tertutup */
  transition: opacity 0.2s ease;
  transition-delay: 0.1s; /* Delay biar smooth */
}

.sidebar:hover .sidebar-content {
  opacity: 1; /* Muncul saat hover */
}

.sidebar h2 {
  text-align: center; margin-bottom: 30px; font-size: 1.8rem; font-weight: 700;
  background: linear-gradient(to right, #60a5fa, #c084fc);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}

/* Tombol New Chat */
#newChat {
  background: linear-gradient(90deg, #2563eb, #4f46e5);
  color: white; border: none; padding: 14px; border-radius: 12px;
  font-weight: 600; cursor: pointer; margin-bottom: 20px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
  transition: transform 0.2s;
}
#newChat:hover { transform: scale(1.02); }

/* History List */
#historyList {
  flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px;
  padding-right: 5px;
}
#historyList::-webkit-scrollbar { width: 4px; }
#historyList::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }

.history-btn {
  background: transparent; 
  color: #cbd5e1; border: 1px solid #334155; 
  padding: 12px 15px; border-radius: 10px;
  text-align: left; cursor: pointer; font-size: 0.85rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  transition: all 0.2s;
}
.history-btn:hover { 
  background: #1e293b; border-color: #60a5fa; color: white;
  transform: translateX(5px);
}

.footer {
  margin-top: 20px; text-align: center; font-size: 0.75rem; color: #64748b;
  border-top: 1px solid #334155; padding-top: 15px;
}

/* --- CHAT AREA --- */
.chat-container {
  flex-grow: 1; display: flex; flex-direction: column;
  background: #0f172a; position: relative;
  width: 100%; /* Full width karena sidebar overlay */
  margin-left: 0; /* Tidak perlu margin */
}

.chat-box {
  flex-grow: 1; overflow-y: auto; padding: 40px 10% 40px 80px; /* Padding kiri lebih besar agar aman dr sidebar trigger */
  display: flex; flex-direction: column; gap: 25px;
  scroll-behavior: smooth;
}

/* Scrollbar Chat */
.chat-box::-webkit-scrollbar { width: 8px; }
.chat-box::-webkit-scrollbar-track { background: #0f172a; }
.chat-box::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }

/* Pesan */
.msg {
  padding: 18px 24px; border-radius: 18px; max-width: 85%;
  line-height: 1.7; font-size: 1rem; position: relative;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #2563eb, #1d4ed8); 
  color: white;
  border-bottom-right-radius: 4px;
}
.ai {
  align-self: flex-start;
  background: #1e293b; color: #e2e8f0;
  border: 1px solid #334155;
  border-bottom-left-radius: 4px;
}

/* Welcome Screen */
.welcome-screen {
  height: 100%; display: flex; flex-direction: column;
  justify-content: center; align-items: center; text-align: center;
}
.welcome-screen h1 {
  font-size: 4rem; margin-bottom: 10px; font-weight: 800;
  background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 20px rgba(56, 189, 248, 0.3));
}
.welcome-screen p { color: #94a3b8; font-size: 1.2rem; margin-bottom: 40px; }

.chips { display: flex; gap: 15px; flex-wrap: wrap; justify-content: center; }
.chip {
  background: #1e293b; border: 1px solid #334155; padding: 12px 24px;
  border-radius: 30px; color: #cbd5e1; cursor: pointer; transition: 0.3s;
  font-size: 0.9rem;
}
.chip:hover { 
  border-color: #38bdf8; color: white; background: #334155; 
  transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

/* Input Area */
form {
  padding: 25px 10% 25px 80px; background: rgba(15, 23, 42, 0.9);
  border-top: 1px solid #1e293b; display: flex; gap: 15px; align-items: center;
  backdrop-filter: blur(10px);
}
textarea {
  flex-grow: 1; background: #1e293b; border: 1px solid #334155;
  border-radius: 16px; padding: 16px; color: white; outline: none;
  font-family: inherit; font-size: 1rem; resize: none; height: 60px;
  transition: border 0.2s;
}
textarea:focus { border-color: #60a5fa; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2); }

button.send {
  height: 60px; width: 60px; border-radius: 16px; border: none;
  background: linear-gradient(135deg, #06b6d4, #0ea5e9); 
  color: white; cursor: pointer; transition: 0.2s;
  display: flex; align-items: center; justify-content: center;
}
button.send:hover { transform: scale(1.05); box-shadow: 0 0 15px rgba(6, 182, 212, 0.5); }
button.send svg { width: 24px; height: 24px; fill: white; }

/* --- KODINGAN WRAPPER --- */
.code-wrapper {
  margin: 15px 0; border-radius: 10px; overflow: hidden;
  border: 1px solid #334155; background: #0d1117;
  font-family: 'Consolas', monospace;
}
.code-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 15px; background: #161b22; border-bottom: 1px solid #334155;
  color: #8b949e; font-size: 0.75rem;
}
.copy-code-btn {
  background: rgba(255,255,255,0.1); border: none; color: #c9d1d9;
  padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 0.75rem;
}
.copy-code-btn:hover { background: #238636; color: white; }

@media (max-width: 768px) {
  .sidebar { display: none; } /* HP: Hide sidebar total (opsional) */
  .chat-box, form { padding-left: 20px; padding-right: 20px; }
}
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-content">
    <h2>Orion AI</h2>
    <button id="newChat">
        <span>+</span> Percakapan Baru
    </button>
    
    <div id="historyList">
        </div>
    
    <div class="footer">Powered by Adrian</div>
  </div>
</div>

<div class="chat-container">
  <div id="chat" class="chat-box">
    <div class="welcome-screen" id="welcome">
        <h1>Halo.</h1>
        <p>Sistem siap. Apa yang ingin kita kerjakan?</p>
        <div class="chips">
            <div class="chip" onclick="isi('Analisa Berita Terkini')">📰 Analisa Berita</div>
            <div class="chip" onclick="isi('Buatkan script Python simple')">🐍 Script Python</div>
            <div class="chip" onclick="isi('Jelaskan teori Black Hole')">🌌 Sains</div>
        </div>
    </div>
  </div>

  <form id="form">
    <textarea id="task" placeholder="Ketik perintah di sini..." rows="1"></textarea>
    <button type="submit" class="send">
        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
    </button>
  </form>
</div>

<script>
// --- RENDERER MARKDOWN & JS UTILS ---
const renderer = new marked.Renderer();
renderer.code = function(code, language) {
  const validLang = !!(language && hljs.getLanguage(language)) ? language : 'plaintext';
  const highlighted = hljs.highlight(code, { language: validLang }).value;
  return `
  <div class="code-wrapper">
    <div class="code-header">
      <span style="color:#58a6ff; font-weight:bold; text-transform:uppercase;">${validLang}</span>
      <button class="copy-code-btn" onclick="copyCodeOnly(this)">Salin Kode</button>
    </div>
    <pre><code class="hljs ${validLang}">${highlighted}</code></pre>
    <div style="display:none" class="raw-code">${code}</div> 
  </div>`;
};
marked.setOptions({ renderer: renderer, breaks: true });

const chat = document.getElementById('chat');
const input = document.getElementById('task');
const historyList = document.getElementById('historyList');
const welcomeScreen = document.getElementById('welcome');

let currentChatId = Date.now();
let chats = JSON.parse(localStorage.getItem('chats_v2')||'{}');
if(!chats[currentChatId]) chats[currentChatId]=[];

function saveChats(){ localStorage.setItem('chats_v2', JSON.stringify(chats)); }
function isi(teks) { input.value = teks; input.focus(); }

window.copyCodeOnly = function(btn) {
    const wrapper = btn.closest('.code-wrapper');
    const rawCode = wrapper.querySelector('.raw-code').innerText;
    navigator.clipboard.writeText(rawCode).then(() => {
        const ori = btn.innerText; btn.innerText = "Tersalin!";
        setTimeout(() => btn.innerText = ori, 2000);
    });
}

function renderChat(){
    chat.innerHTML = '';
    if(!chats[currentChatId] || chats[currentChatId].length === 0){
        chat.appendChild(welcomeScreen);
        welcomeScreen.style.display = 'flex';
        return;
    } 
    if(chat.contains(welcomeScreen)) welcomeScreen.remove(); 

    for(const msg of chats[currentChatId]){
        const div = document.createElement('div');
        div.className = 'msg ' + msg.sender;
        if(msg.sender === 'ai') div.innerHTML = marked.parse(msg.text);
        else div.innerText = msg.text;
        chat.appendChild(div);
    }
    chat.scrollTop = chat.scrollHeight;
}

function renderHistory(){
    historyList.innerHTML='';
    Object.keys(chats).sort((a,b)=>b-a).forEach(id=>{
        if(chats[id].length === 0 && id != currentChatId) return;
        let txt = 'Percakapan Baru';
        const u = chats[id].find(m=>m.sender==='user');
        if(u) txt = u.text.slice(0,22)+'...';
        
        const btn = document.createElement('button');
        btn.className = 'history-btn'; 
        btn.innerText = txt;
        btn.onclick = () => { currentChatId = id; renderChat(); };
        historyList.appendChild(btn);
    });
}

document.getElementById('newChat').onclick = () => {
    currentChatId = Date.now();
    chats[currentChatId] = [];
    saveChats();
    renderChat(); renderHistory();
};

document.getElementById('form').addEventListener('submit', async e => {
    e.preventDefault();
    const q = input.value.trim();
    if(!q) return;
    
    if(!chats[currentChatId]) chats[currentChatId] = [];
    chats[currentChatId].push({sender:'user', text:q});
    saveChats(); renderChat(); renderHistory();
    input.value='';
    
    chats[currentChatId].push({sender:'ai', text:'_Sedang berpikir..._'});
    renderChat();

    try {
        const res = await fetch('/ask', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({question: q})
        });
        const data = await res.json();
        chats[currentChatId].pop(); 
        chats[currentChatId].push({sender:'ai', text: data.answer});
        saveChats(); renderChat();
    } catch(err) {
        chats[currentChatId].pop();
        chats[currentChatId].push({sender:'ai', text: "Error: "+err});
        saveChats(); renderChat();
    }
});

renderHistory();
</script>
</body>
</html>
"""

def get_latest_news(query):
    try:
        url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=id&gl=ID&ceid=ID:id"
        r = requests.get(url)
        items = re.findall(r"<title>(.*?)</title><link>(.*?)</link>", r.text)
        if len(items)>1:
            news=[]
            for title,link in items[1:5]: news.append(f"🔹 **{title}**\n[Baca Selengkapnya]({link})")
            return "### 📰 Berita Terbaru:\n" + "\n".join(news)
        return "Tidak ada berita ditemukan."
    except: return "Gagal mengambil berita."

@app.route("/")
def home(): return render_template_string(html)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question","")
    
    if "berita" in question.lower() or "news" in question.lower():
        topic = question.replace("berita","").replace("terbaru","").strip()
        news_data = get_latest_news(topic if topic else "Indonesia")
        return jsonify({"answer": news_data})

    full_prompt = f"{SYSTEM_PROMPT}\nUser: {question}\nAI:"
    
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }

    try:
        response = requests.post(AI_URL, json=payload)
        if response.status_code == 429: return jsonify({"answer": "⚠️ Kuota API habis. Coba lagi nanti."})
        if response.status_code != 200: return jsonify({"answer": f"⚠️ Error: {response.text}"})
        
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
             ans = data["candidates"][0]["content"]["parts"][0]["text"]
             return jsonify({"answer": ans})
        else: return jsonify({"answer": "Maaf, saya diam."})
    except Exception as e: return jsonify({"answer": f"Error: {str(e)}"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
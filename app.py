from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

# ==========================================
# ⚠️ KONFIGURASI API KEY (WAJIB DIISI)
# ==========================================
API_KEY = "AIzaSyCB8vD108_km8EV566MlpDfI4Sj4Vu_zGI" 

AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

SYSTEM_PROMPT = "Kamu adalah Orion AI. Jawab singkat, jelas, dan membantu."

# ==========================================
# 🎨 FRONTEND (STRIP BUTTON + VISIBLE EDGE)
# ==========================================
html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>🌌 Orion AI by Adrian</title>

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

<style>
/* --- RESET --- */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Poppins', sans-serif;
  height: 100dvh; 
  width: 100%;
  overflow: hidden; 
  background: #0f172a; color: #e2e8f0;
  display: flex;
}

/* --- TOMBOL STRIP MENU (KIRI ATAS) --- */
.menu-toggle {
  position: fixed;
  top: 20px; left: 0;
  z-index: 3000;
  
  /* Desain Tombol Strip */
  width: 45px; height: 40px;
  background: #1e293b;
  border: 1px solid #334155;
  border-left: none; /* Nempel pinggir */
  border-radius: 0 10px 10px 0; /* Melengkung kanan */
  
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: #38bdf8; /* Warna Ikon */
  box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
  transition: transform 0.2s;
}

/* Efek tekan */
.menu-toggle:active { transform: scale(0.95); }

/* Sembunyikan tombol ini saat menu terbuka (biar bersih) */
body.menu-open .menu-toggle { opacity: 0; pointer-events: none; }


/* --- SIDEBAR --- */
.sidebar {
  position: fixed; left: 0; top: 0; bottom: 0;
  z-index: 2000;
  width: 280px; 
  background: #1e293b;
  border-right: 1px solid #334155;
  
  /* Default sembunyi di kiri */
  transform: translateX(-100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  display: flex; flex-direction: column; padding: 20px;
}

/* Saat Menu Terbuka */
.sidebar.active {
  transform: translateX(0);
  box-shadow: 5px 0 50px rgba(0,0,0,0.5);
}

/* Komponen Sidebar */
.sidebar h2 {
  text-align: center; margin-bottom: 20px; font-size: 1.8rem; font-weight: 700;
  background: linear-gradient(to right, #60a5fa, #c084fc);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
#newChat {
  background: linear-gradient(90deg, #2563eb, #4f46e5);
  color: white; border: none; padding: 12px; border-radius: 10px;
  font-weight: 600; cursor: pointer; margin-bottom: 15px;
  display: flex; align-items: center; gap:10px;
}
#historyList { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.history-btn {
  background: transparent; color: #cbd5e1; border: 1px solid #334155; 
  padding: 12px; border-radius: 8px; text-align: left; cursor: pointer; 
  font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis;
}
.footer { margin-top:auto; text-align:center; font-size:0.7rem; color:#64748b; }


/* --- OVERLAY GELAP --- */
.overlay {
  position: fixed; top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.7); z-index: 1500;
  display: none; backdrop-filter: blur(2px);
}
.overlay.active { display: block; }


/* --- DESKTOP MODE (> 768px) --- */
@media (min-width: 769px) {
  .menu-toggle { display: none; } /* Hapus tombol di PC */
  .sidebar { 
    transform: translateX(0); /* Selalu muncul */
    width: 280px;
    position: relative; /* Gak nimpah konten */
  }
  .overlay { display: none !important; }
  .chat-container { width: calc(100% - 280px); }
}


/* --- CHAT AREA --- */
.chat-container {
  flex-grow: 1; display: flex; flex-direction: column;
  background: #0f172a; width: 100%; height: 100dvh;
}

.chat-box {
  flex-grow: 1; overflow-y: auto; padding: 70px 20px 20px 20px; /* Padding atas besar biar ga ketutup tombol menu */
  display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth;
}
/* Di PC padding atas normal */
@media (min-width: 769px) { .chat-box { padding-top: 20px; } }

.msg {
  padding: 15px 20px; border-radius: 15px; max-width: 90%;
  line-height: 1.6; font-size: 0.95rem; word-wrap: break-word;
}
.user { align-self: flex-end; background: #2563eb; color: white; border-bottom-right-radius: 2px; }
.ai { align-self: flex-start; background: #1e293b; border: 1px solid #334155; border-bottom-left-radius: 2px; }


/* --- INPUT FORM --- */
form {
  padding: 15px; background: #1e293b; border-top: 1px solid #334155;
  display: flex; gap: 10px; align-items: center; flex-shrink: 0;
  padding-bottom: max(20px, env(safe-area-inset-bottom));
}
textarea {
  flex-grow: 1; background: #0f172a; border: 1px solid #334155;
  border-radius: 20px; padding: 12px 15px; color: white; outline: none;
  font-family: inherit; resize: none; height: 50px; font-size: 16px;
}
textarea:focus { border-color: #38bdf8; }
button.send {
  height: 50px; width: 50px; border-radius: 50%; border: none;
  background: #06b6d4; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center;
}

/* UTILS */
.code-wrapper { background: #0d1117; border-radius: 8px; margin: 10px 0; border: 1px solid #334155; overflow: hidden; }
.code-header { padding: 5px 10px; background: #161b22; color: #8b949e; font-size: 0.7rem; display: flex; justify-content: space-between; }
.code-wrapper pre { padding: 10px; overflow-x: auto; }
.welcome-screen { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
.welcome-screen h1 { font-size: 2rem; background: linear-gradient(to right, #38bdf8, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
.welcome-screen p { color: #94a3b8; font-size: 0.9rem; margin-bottom: 30px; }
.chips { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; width: 100%; }
.chip { background: #1e293b; border: 1px solid #334155; padding: 10px 20px; border-radius: 25px; color: #cbd5e1; cursor: pointer; transition: 0.2s; font-size: 0.85rem; }

</style>
</head>
<body>

<button class="menu-toggle" onclick="toggleMenu()">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
</button>

<div class="overlay" id="overlay" onclick="toggleMenu()"></div>

<div class="sidebar" id="sidebar">
    <h2>Orion AI</h2>
    <button id="newChat"><span>+</span> Chat Baru</button>
    <div id="historyList"></div>
    <div class="footer">Di Buat Adrian</div>
</div>

<div class="chat-container">
  <div id="chat" class="chat-box">
    <div class="welcome-screen" id="welcome">
        <h1>Halo, Kamu!</h1>
        <p>Tekan tombol menu di pojok kiri atas.</p>
        <div class="chips">
            <div class="chip" onclick="isi('Berita hari ini')">📰 Berita</div>
            <div class="chip" onclick="isi('Buatkan kodingan HTML')">💻 Coding</div>
            <div class="chip" onclick="isi('Ide konten Instagram')">📸 Sosmed</div>
            <div class="chip" onclick="isi('Jelaskan apa itu AI')">🤖 Info AI</div>
        </div>
    </div>
  </div>

  <form id="form">
    <textarea id="task" placeholder="Ketik pesan..." rows="1"></textarea>
    <button type="submit" class="send">➤</button>
  </form>
</div>

<script>
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const body = document.body;

function toggleMenu() {
    const isActive = sidebar.classList.contains('active');
    if (isActive) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        body.classList.remove('menu-open');
    } else {
        sidebar.classList.add('active');
        overlay.classList.add('active');
        body.classList.add('menu-open');
    }
}

// LOGIC CHAT
const renderer = new marked.Renderer();
renderer.code = function(code, language) {
  const validLang = !!(language && hljs.getLanguage(language)) ? language : 'plaintext';
  const highlighted = hljs.highlight(code, { language: validLang }).value;
  return `<div class="code-wrapper"><div class="code-header"><span>${validLang}</span></div><pre><code class="hljs ${validLang}">${highlighted}</code></pre></div>`;
};
marked.setOptions({ renderer: renderer, breaks: true });

const chat = document.getElementById('chat');
const input = document.getElementById('task');
const historyList = document.getElementById('historyList');
const welcomeScreen = document.getElementById('welcome');

let currentChatId = Date.now();
let chats = JSON.parse(localStorage.getItem('chats_v13')||'{}');
if(!chats[currentChatId]) chats[currentChatId]=[];

function saveChats(){ localStorage.setItem('chats_v13', JSON.stringify(chats)); }
function isi(teks) { input.value = teks; input.focus(); }

function renderChat(){
    chat.innerHTML = '';
    if(!chats[currentChatId] || chats[currentChatId].length === 0){
        chat.appendChild(welcomeScreen); welcomeScreen.style.display = 'flex'; return;
    }
    if(chat.contains(welcomeScreen)) welcomeScreen.remove();
    for(const msg of chats[currentChatId]){
        const div = document.createElement('div'); div.className = 'msg ' + msg.sender;
        div.innerHTML = msg.sender === 'ai' ? marked.parse(msg.text) : msg.text;
        chat.appendChild(div);
    }
    chat.scrollTop = chat.scrollHeight;
}

function renderHistory(){
    historyList.innerHTML='';
    Object.keys(chats).sort((a,b)=>b-a).forEach(id=>{
        if(chats[id].length === 0 && id != currentChatId) return;
        let txt = chats[id].find(m=>m.sender==='user')?.text.slice(0,18)+'...' || 'Chat Baru';
        const btn = document.createElement('button');
        btn.className = 'history-btn'; btn.innerText = txt;
        btn.onclick = (e) => { 
            currentChatId = id; renderChat(); 
            if(window.innerWidth <= 768) toggleMenu();
        };
        historyList.appendChild(btn);
    });
}

document.getElementById('newChat').onclick = (e) => {
    currentChatId = Date.now(); chats[currentChatId] = []; saveChats(); renderChat(); renderHistory();
    if(window.innerWidth <= 768) toggleMenu();
};

document.getElementById('form').addEventListener('submit', async e => {
    e.preventDefault();
    const q = input.value.trim(); if(!q) return;
    if(!chats[currentChatId]) chats[currentChatId] = [];
    chats[currentChatId].push({sender:'user', text:q});
    saveChats(); renderChat(); renderHistory(); input.value='';
    
    chats[currentChatId].push({sender:'ai', text:'_Sedang mengetik..._'}); renderChat();

    try {
        const res = await fetch('/ask', {
            method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question: q})
        });
        const data = await res.json();
        chats[currentChatId].pop(); 
        
        if(data.answer && data.answer.startsWith("⚠️")) {
             chats[currentChatId].push({sender:'ai', text: "**SYSTEM ERROR:** " + data.answer}); 
        } else {
             chats[currentChatId].push({sender:'ai', text: data.answer});
        }
        
        saveChats(); renderChat();
    } catch(err) {
        chats[currentChatId].pop(); 
        chats[currentChatId].push({sender:'ai', text: "⚠️ **Koneksi Error:** Gagal menghubungi server."}); 
        renderChat();
    }
});

renderHistory();
</script>
</body>
</html>
"""

@app.route("/")
def home(): return render_template_string(html)

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("question","")
    if "PASTE_API_KEY" in API_KEY:
         return jsonify({"answer": "⚠️ **API Key Belum Diisi.**\nSilakan isi API KEY di kode Python."})

    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\nUser:{q}\nAI:"}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }

    try:
        r = requests.post(AI_URL, json=payload)
        if r.status_code == 403:
             return jsonify({"answer": "⚠️ **API Key Ditolak.**\nGoogle memblokir key ini. Ganti dengan yang baru."})
        if r.status_code != 200:
             return jsonify({"answer": f"⚠️ API Error ({r.status_code}): {r.text}"})
        data = r.json()
        if "candidates" in data and len(data["candidates"]) > 0:
             return jsonify({"answer": data["candidates"][0]["content"]["parts"][0]["text"]})
        else:
             return jsonify({"answer": "⚠️ Tidak ada jawaban."})
    except Exception as e:
        return jsonify({"answer": f"⚠️ Server Error: {str(e)}"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
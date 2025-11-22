from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

# ==========================================
# ⚠️ KONFIGURASI API KEY
# ==========================================
API_KEY = "AIzaSyCH1myR7PH_mJM_Xo94otL_31eYUoXkh0s"
AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

SYSTEM_PROMPT = "Kamu adalah Orion AI. Jawab singkat, jelas, dan membantu."

# ==========================================
# 🎨 FRONTEND (INVISIBLE SIDEBAR + CHIPS)
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
  height: 100dvh; /* Full layar HP */
  width: 100%;
  overflow: hidden; 
  background: #0f172a; color: #e2e8f0;
  display: flex;
}

/* --- SIDEBAR (INVISIBLE TOUCH AREA) --- */
.sidebar {
  position: fixed; left: 0; top: 0; bottom: 0;
  z-index: 2000;
  
  /* Area sentuh transparan selebar 30px di kiri */
  width: 30px; 
  background: transparent; 
  border: none; 
  cursor: pointer;
  
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s;
  overflow: hidden;
}

/* Saat Menu Terbuka */
.sidebar.active {
  width: 85%; 
  max-width: 300px;
  background: #1e293b; 
  box-shadow: 10px 0 50px rgba(0,0,0,0.8);
  border-right: 1px solid #334155;
}

.sidebar-content {
  width: 280px; height: 100%; padding: 20px;
  display: flex; flex-direction: column;
  opacity: 0; transition: opacity 0.2s;
  min-width: 280px; 
}
.sidebar.active .sidebar-content { opacity: 1; transition-delay: 0.1s; }

/* Desktop Mode */
@media (min-width: 769px) {
  .sidebar { width: 10px; }
  .sidebar:hover { width: 300px; background: #1e293b; }
  .sidebar:hover .sidebar-content { opacity: 1; }
}

/* Overlay */
.overlay {
  position: fixed; top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.8); z-index: 1500;
  display: none; backdrop-filter: blur(3px);
}
.overlay.active { display: block; }


/* --- CHAT AREA --- */
.chat-container {
  flex-grow: 1; display: flex; flex-direction: column;
  background: #0f172a; width: 100%; height: 100dvh;
  padding-left: 10px; 
}

.chat-box {
  flex-grow: 1; overflow-y: auto; padding: 20px;
  display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth;
}

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

/* --- COMPONENTS & CHIPS --- */
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
.code-wrapper { background: #0d1117; border-radius: 8px; margin: 10px 0; border: 1px solid #334155; overflow: hidden; }
.code-header { padding: 5px 10px; background: #161b22; color: #8b949e; font-size: 0.7rem; display: flex; justify-content: space-between; }
.code-wrapper pre { padding: 10px; overflow-x: auto; }

/* STYLE LAYAR SAMBUTAN (Updated) */
.welcome-screen { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
.welcome-screen h1 { font-size: 2rem; background: linear-gradient(to right, #38bdf8, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
.welcome-screen p { color: #94a3b8; font-size: 0.9rem; margin-bottom: 30px; }

/* STYLE SUGGESTION CHIPS */
.chips { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; width: 100%; }
.chip {
  background: #1e293b; border: 1px solid #334155; padding: 10px 20px;
  border-radius: 25px; color: #cbd5e1; cursor: pointer; transition: 0.2s;
  font-size: 0.85rem;
}
.chip:hover { border-color: #38bdf8; background: #334155; color: white; transform: translateY(-2px); }

</style>
</head>
<body>

<div class="overlay" id="overlay" onclick="tutupMenu()"></div>

<div class="sidebar" id="sidebar" onclick="bukaMenu()">
  <div class="sidebar-content">
    <h2>Orion AI</h2>
    <button id="newChat"><span>+</span> Chat Baru</button>
    <div id="historyList"></div>
    <div style="margin-top:auto; text-align:center; font-size:0.7rem; color:#64748b;">By Adrian</div>
  </div>
</div>

<div class="chat-container">
  <div id="chat" class="chat-box">
    <div class="welcome-screen" id="welcome">
        <h1>Halo, Kamu!</h1>
        <p>Ada yang bisa Orion bantu?</p>
        
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

function bukaMenu() {
    if (!sidebar.classList.contains('active')) {
        sidebar.classList.add('active');
        overlay.classList.add('active');
    }
}
function tutupMenu() {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
}
document.querySelector('.sidebar-content').addEventListener('click', function(e) { e.stopPropagation(); });

// --- CHAT ENGINE ---
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
let chats = JSON.parse(localStorage.getItem('chats_v10')||'{}');
if(!chats[currentChatId]) chats[currentChatId]=[];

function saveChats(){ localStorage.setItem('chats_v10', JSON.stringify(chats)); }
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
            e.stopPropagation();
            currentChatId = id; renderChat(); 
            if(window.innerWidth <= 768) tutupMenu();
        };
        historyList.appendChild(btn);
    });
}

document.getElementById('newChat').onclick = (e) => {
    e.stopPropagation();
    currentChatId = Date.now(); chats[currentChatId] = []; saveChats(); renderChat(); renderHistory();
    if(window.innerWidth <= 768) tutupMenu();
};

document.getElementById('form').addEventListener('submit', async e => {
    e.preventDefault();
    const q = input.value.trim(); if(!q) return;
    if(!chats[currentChatId]) chats[currentChatId] = [];
    chats[currentChatId].push({sender:'user', text:q});
    saveChats(); renderChat(); renderHistory(); input.value='';
    
    chats[currentChatId].push({sender:'ai', text:'_..._'}); renderChat();

    try {
        const res = await fetch('/ask', {
            method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question: q})
        });
        const data = await res.json();
        chats[currentChatId].pop(); chats[currentChatId].push({sender:'ai', text: data.answer});
        saveChats(); renderChat();
    } catch(err) {
        chats[currentChatId].pop(); chats[currentChatId].push({sender:'ai', text: "Error."}); renderChat();
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
    payload = {"contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\nUser:{q}\nAI:"}]}]}
    try:
        r = requests.post(AI_URL, json=payload)
        return jsonify({"answer": r.json()["candidates"][0]["content"]["parts"][0]["text"]})
    except: return jsonify({"answer": "Maaf, error."})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
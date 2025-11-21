from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

# ==========================================
# ⚠️ KONFIGURASI API KEY
# ==========================================
API_KEY = "AIzaSyD1tV5Zav3lH3_doWRauEnQ2cQmleR8c5k"

# Menggunakan Model Gemini 2.0 Flash
AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# ==========================================
# 🎨 FRONTEND (DESAIN ORION AI FINAL)
# ==========================================
html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌌 Orion AI by Adrian</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

<style>
/* --- GAYA DASAR --- */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  height: 100vh; overflow: hidden; background: #0f172a; color: #e2e8f0;
}

/* Sidebar Styling */
.sidebar {
  position: fixed; left: -280px; top: 0; width: 280px; height: 100%;
  background: rgba(30, 41, 59, 0.85);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(148, 163, 184, 0.1);
  display: flex; flex-direction: column;
  transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1); z-index: 1000;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
}
.sidebar:hover { left: 0; }

.sidebar h2 {
  text-align: center; font-size: 1.75rem; margin: 32px 0 24px;
  background: linear-gradient(135deg, #38bdf8, #a855f7, #facc15);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  font-weight: 700; letter-spacing: 0.5px;
}

.sidebar button {
  margin: 6px 12px; padding: 12px 16px; border: none; border-radius: 12px;
  background: rgba(37, 99, 235, 0.8);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  color: white; cursor: pointer; text-align: left;
  width: calc(100% - 24px); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9rem; font-weight: 500; border: 1px solid rgba(59, 130, 246, 0.3);
}
.sidebar button:hover {
  background: rgba(59, 130, 246, 0.9); transform: translateX(4px) scale(1.02);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4); border-color: rgba(59, 130, 246, 0.6);
}

#historyList { flex-grow: 1; overflow-y: auto; margin-top: 8px; padding-right: 4px; }
#historyList::-webkit-scrollbar { width: 6px; }
#historyList::-webkit-scrollbar-track { background: rgba(51, 65, 85, 0.3); border-radius: 10px; }
#historyList::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.4); border-radius: 10px; }

.sidebar .footer {
  text-align: center; font-size: 0.75rem; margin-top: auto; padding: 20px 10px;
  color: rgba(226, 232, 240, 0.6); border-top: 1px solid rgba(148, 163, 184, 0.1); font-weight: 300;
}

/* Chat Container */
.chat-container {
  width: 100%; height: 100vh; display: flex; flex-direction: column;
  background: radial-gradient(circle at 20% 20%, #0f172a, #1e293b 60%, #020617);
  transition: margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1); position: relative;
}
.chat-container::before {
  content: ''; position: fixed; left: 0; top: 0; width: 20px; height: 100%; z-index: 999; background: transparent;
}

.chat-box {
  flex-grow: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px;
}
.chat-box::-webkit-scrollbar { width: 8px; }
.chat-box::-webkit-scrollbar-track { background: rgba(30, 41, 59, 0.3); }
.chat-box::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.4); border-radius: 10px; }

/* Message Styling */
.msg {
  padding: 14px 18px; border-radius: 16px; max-width: 80%; word-wrap: break-word;
  line-height: 1.6; font-size: 0.95rem; position: relative;
  animation: messageSlide 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Fix untuk Markdown List dan Paragraf */
.msg p { margin-bottom: 10px; }
.msg p:last-child { margin-bottom: 0; }
.msg ul, .msg ol { margin-left: 20px; margin-bottom: 10px; }
.msg li { margin-bottom: 5px; }
.msg strong { font-weight: 700; color: #fff; }
.msg pre { margin: 10px 0; padding: 12px; background: #1e1e1e; border-radius: 8px; overflow-x: auto; }
.msg code { font-family: 'Consolas', monospace; font-size: 0.9em; }

/* Tombol Salin */
.copy-btn {
    position: absolute; top: 5px; right: 5px;
    background: rgba(255,255,255,0.1); border: none; color: #cbd5e1;
    padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; cursor: pointer;
    transition: 0.2s; display: none;
}
.msg:hover .copy-btn { display: block; }
.copy-btn:hover { background: rgba(255,255,255,0.2); color: white; }

@keyframes messageSlide { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.user {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.9), rgba(59, 130, 246, 0.9));
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  color: white; align-self: flex-end; border: 1px solid rgba(59, 130, 246, 0.3); margin-left: auto;
}
.ai {
  background: rgba(148, 163, 184, 0.08); backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(148, 163, 184, 0.15);
  color: #e2e8f0; align-self: flex-start; margin-right: auto;
}

/* Form Styling */
form {
  display: flex; padding: 16px; background: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(148, 163, 184, 0.1); gap: 12px;
}
textarea {
  flex-grow: 1; border: none; border-radius: 14px; padding: 14px 18px;
  font-size: 0.95rem; resize: none; outline: none;
  background: rgba(51, 65, 85, 0.6); backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px); color: #f1f5f9; font-family: inherit;
  transition: all 0.3s ease; border: 1px solid rgba(148, 163, 184, 0.2); line-height: 1.5;
}
textarea:focus {
  background: rgba(51, 65, 85, 0.8); border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
textarea::placeholder { color: rgba(203, 213, 225, 0.5); }

button.send {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.9), rgba(14, 165, 233, 0.9));
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border: none; border-radius: 14px; color: white; font-weight: 600;
  padding: 14px 28px; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.95rem; border: 1px solid rgba(6, 182, 212, 0.3);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}
button.send:hover {
  background: linear-gradient(135deg, rgba(6, 182, 212, 1), rgba(14, 165, 233, 1));
  transform: translateY(-2px); box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
}
button.send:active { transform: translateY(0); box-shadow: 0 2px 8px rgba(6, 182, 212, 0.4); }
audio { display: none; }

/* Layar Sambutan */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; text-align: center; animation: fadeIn 0.5s ease; color: #e2e8f0;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.empty-state h1 {
  font-size: 2.5rem; margin-bottom: 16px; font-weight: 700;
  background: linear-gradient(135deg, #38bdf8, #a855f7, #facc15);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.empty-state p { font-size: 1.1rem; max-width: 500px; line-height: 1.6; color: rgba(226, 232, 240, 0.8); }
.suggestion-chips {
  display: flex; gap: 10px; margin-top: 30px; flex-wrap: wrap; justify-content: center;
}
.chip {
  background: rgba(51, 65, 85, 0.5);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(148, 163, 184, 0.2); color: #f1f5f9;
  padding: 10px 18px; border-radius: 20px; cursor: pointer; font-size: 0.9rem;
  transition: all 0.3s ease;
}
.chip:hover {
  background: rgba(59, 130, 246, 0.3); border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  body { height: 100vh; height: 100dvh; }
  .sidebar { width: 260px; left: -260px; }
  .sidebar:hover { left: 0; }
  .chat-container { margin-left: 0; width: 100%; height: 100vh; height: 100dvh; }
  .chat-box { padding: 12px; padding-bottom: 80px; }
  .msg { max-width: 85%; font-size: 0.9rem; padding: 12px 14px; }
  form { padding: 10px; position: fixed; bottom: 0; left: 0; right: 0; background: rgba(30, 41, 59, 0.95); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
  textarea { font-size: 0.9rem; padding: 12px 14px; }
  button.send { padding: 12px 20px; font-size: 0.9rem; }
  .empty-state h1 { font-size: 2rem; }
}
@media (max-width: 480px) {
  .msg { max-width: 90%; } .sidebar h2 { font-size: 1.5rem; }
}
</style>
</head>
<body>

<div class="sidebar" id="sidebar">
  <h2>Orion AI</h2>
  <button id="newChat">+ Percakapan Baru</button>
  <div id="historyList"></div>
  <div class="footer">Dibuat oleh Adrian</div>
</div>

<div class="chat-container" id="chatContainer">
  <audio id="bgMusic" loop autoplay>
    <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-17.mp3" type="audio/mpeg">
  </audio>
  <div id="chat" class="chat-box"></div>
  <form id="form">
    <textarea id="task" placeholder="Ketik pertanyaan atau topik berita..." rows="1"></textarea>
    <button type="submit" class="send">Kirim</button>
  </form>
</div>

<script>
const chat = document.getElementById('chat');
const form = document.getElementById('form');
const input = document.getElementById('task');
const historyList = document.getElementById('historyList');
const newChatBtn = document.getElementById('newChat');
const sidebar = document.getElementById('sidebar');

let currentChatId = Date.now();
let chats = JSON.parse(localStorage.getItem('chats')||'{}');
if(!chats[currentChatId]) chats[currentChatId] = [];

function saveChats(){ localStorage.setItem('chats', JSON.stringify(chats)); }

// Fungsi Copy Text
function copyText(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = btn.innerText;
        btn.innerText = "Tersalin";
        setTimeout(() => { btn.innerText = originalText; }, 1500);
    });
}

function renderChat(){
    chat.innerHTML = '';
    
    if(!chats[currentChatId] || chats[currentChatId].length === 0){
        chat.innerHTML = `
            <div class="empty-state">
                <h1>Halo, Adrian!</h1>
                <p>Saya Orion AI. Ada yang bisa saya bantu kerjakan hari ini?</p>
                <div class="suggestion-chips">
                    <div class="chip" onclick="fillInput('Carikan berita terbaru hari ini di Indonesia')">Berita Hari Ini</div>
                    <div class="chip" onclick="fillInput('Buatkan ide konten Instagram tentang teknologi')">Ide Konten IG</div>
                    <div class="chip" onclick="fillInput('Jelaskan secara singkat apa itu AI')">Apa itu AI?</div>
                </div>
            </div>
        `;
        return;
    }

    for(const msg of chats[currentChatId]){
        const div = document.createElement('div');
        div.className = 'msg ' + msg.sender;
        
        // Parse Markdown
        let content = marked.parse(msg.text);
        div.innerHTML = content;

        // Tambahkan Tombol Salin jika itu pesan AI
        if(msg.sender === 'ai'){
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.innerText = 'Salin';
            copyBtn.onclick = () => copyText(msg.text, copyBtn);
            div.appendChild(copyBtn);
        }

        chat.appendChild(div);
    }
    
    // Syntax Highlighting
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    chat.scrollTop = chat.scrollHeight;
}

function renderHistory(){
    historyList.innerHTML='';
    Object.keys(chats).sort((a,b)=>b-a).forEach(id=>{
        if(chats[id].length === 0 && id != currentChatId) return; 

        let firstMsg = 'Percakapan Baru';
        const userMsg = chats[id].find(m => m.sender === 'user');
        if(userMsg){
            firstMsg = userMsg.text.length>25 ? userMsg.text.slice(0,25)+'...' : userMsg.text;
        } else if (chats[id].length > 0) {
             firstMsg = "Sesi " + new Date(parseInt(id)).toLocaleTimeString('id-ID', {hour: '2-digit', minute:'2-digit'});
        }
        
        const btn=document.createElement('button');
        btn.innerText = firstMsg;
        btn.onclick=()=>{ currentChatId=id; renderChat(); };
        historyList.appendChild(btn);
    });
}

window.fillInput = (text) => {
    input.value = text; input.focus();
}

newChatBtn.onclick = ()=>{
    currentChatId = Date.now();
    chats[currentChatId] = [];
    saveChats();
    renderChat();
    renderHistory();
};

document.body.addEventListener('mousemove', e=>{
    if(e.clientX <= 20){ sidebar.style.left = '0'; } 
    else if(!sidebar.matches(':hover')){ sidebar.style.left = '-280px'; }
});
document.body.addEventListener('touchstart', e=>{
    if(e.touches[0].clientX <= 20){ sidebar.style.left = '0'; }
});

form.addEventListener('submit',async e=>{
    e.preventDefault();
    const question = input.value.trim();
    if(!question) return;
    
    if(!chats[currentChatId]) chats[currentChatId] = [];
    
    chats[currentChatId].push({sender:'user', text:question});
    saveChats();
    renderChat();
    renderHistory();
    
    input.value='';
    const loader={sender:'ai', text:'_Sedang mengetik..._'};
    chats[currentChatId].push(loader);
    renderChat();

    const res = await fetch('/ask',{
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question})
    });
    const data = await res.json();
    chats[currentChatId].pop();
    chats[currentChatId].push({sender:'ai', text:data.answer||'Terjadi kesalahan.'});
    saveChats();
    renderChat();
});

renderHistory();
renderChat();
</script>

</body>
</html>
"""

def get_latest_news(query):
    try:
        url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=id&gl=ID&ceid=ID:id"
        r = requests.get(url)
        if r.status_code != 200: return "Gagal mengambil berita terbaru."
        items = re.findall(r"<title>(.*?)</title><link>(.*?)</link>", r.text)
        if len(items)>1:
            news=[]
            for title,link in items[1:5]: news.append(f"📰 {title}\n🔗 {link}")
            return "\n\n".join(news)
        return "Tidak ada berita terbaru ditemukan."
    except Exception as e:
        return f"Gagal ambil berita: {str(e)}"

@app.route("/")
def home(): return render_template_string(html)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question","")
    try:
        if "berita" in question.lower() or "news" in question.lower():
            topic = question.replace("berita","").replace("terbaru","").strip()
            news_data = get_latest_news(topic if topic else "Indonesia")
            return jsonify({"answer": news_data})
        
        payload={"contents":[{"parts":[{"text":f"{question}"}]}]}
        response=requests.post(AI_URL,json=payload)
        
        # ⚠️ PENANGANAN LIMIT KUOTA (429) ⚠️
        if response.status_code == 429:
             return jsonify({"answer": "⚠️ Maaf Bang , kuota gratis hari ini sudah habis. Mohon tunggu beberapa saat atau coba lagi besok ya! 🙏"})
             
        data=response.json()
        if "candidates" in data:
             answer = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
             answer = "Maaf, saya sedang mengalami gangguan koneksi."
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer":f"Error: {str(e)}"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
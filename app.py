from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

API_KEY = "AIzaSyD1tV5Zav3lH3_doWRauEnQ2cQmleR8c5k"
AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌌 Orion AI by Adrian</title>
<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  height: 100vh;
  overflow: hidden;
  background: #0f172a;
}

/* Sidebar Styling */
.sidebar {
  position: fixed;
  left: -280px;
  top: 0;
  width: 280px;
  height: 100%;
  background: rgba(30, 41, 59, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(148, 163, 184, 0.1);
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
}

.sidebar:hover {
  left: 0;
}

.sidebar h2 {
  text-align: center;
  font-size: 1.75rem;
  margin: 32px 0 24px;
  background: linear-gradient(135deg, #38bdf8, #a855f7, #facc15);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  letter-spacing: 0.5px;
  filter: drop-shadow(0 2px 8px rgba(168, 85, 247, 0.3));
}

.sidebar button {
  margin: 6px 16px;
  padding: 12px 16px;
  border: none;
  border-radius: 12px;
  background: rgba(37, 99, 235, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  cursor: pointer;
  text-align: left;
  width: calc(100% - 32px);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.95rem;
  font-weight: 500;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.sidebar button:hover {
  background: rgba(59, 130, 246, 0.9);
  transform: translateX(4px) scale(1.02);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
  border-color: rgba(59, 130, 246, 0.6);
}

.sidebar button:active {
  transform: translateX(4px) scale(0.98);
}

.sidebar #newChat {
  background: rgba(6, 182, 212, 0.8);
  border-color: rgba(6, 182, 212, 0.3);
  font-weight: 600;
}

.sidebar #newChat:hover {
  background: rgba(6, 182, 212, 1);
  box-shadow: 0 4px 16px rgba(6, 182, 212, 0.5);
  border-color: rgba(6, 182, 212, 0.6);
}

.sidebar .close-btn {
  display: none;
}

#historyList {
  flex-grow: 1;
  overflow-y: auto;
  margin-top: 8px;
  padding-right: 4px;
}

#historyList::-webkit-scrollbar {
  width: 6px;
}

#historyList::-webkit-scrollbar-track {
  background: rgba(51, 65, 85, 0.3);
  border-radius: 10px;
}

#historyList::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.4);
  border-radius: 10px;
}

#historyList::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.6);
}

.sidebar .footer {
  text-align: center;
  font-size: 0.75rem;
  margin-top: auto;
  padding: 20px 10px;
  color: rgba(226, 232, 240, 0.6);
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  font-weight: 300;
}

/* Chat Container */
.chat-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at 20% 20%, #0f172a, #1e293b 60%, #020617);
  transition: margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

/* Hover Zone - Area transparan di kiri untuk memicu sidebar */
.chat-container::before {
  content: '';
  position: fixed;
  left: 0;
  top: 0;
  width: 20px;
  height: 100%;
  z-index: 999;
  background: transparent;
}

.chat-box {
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-box::-webkit-scrollbar {
  width: 8px;
}

.chat-box::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.3);
}

.chat-box::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.4);
  border-radius: 10px;
}

.chat-box::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.6);
}

/* Message Styling */
.msg {
  padding: 14px 18px;
  border-radius: 16px;
  max-width: 75%;
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 0.95rem;
  animation: messageSlide 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@keyframes messageSlide {
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
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.9), rgba(59, 130, 246, 0.9));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  align-self: flex-end;
  border: 1px solid rgba(59, 130, 246, 0.3);
  margin-left: auto;
}

.ai {
  background: rgba(148, 163, 184, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(148, 163, 184, 0.15);
  color: #e2e8f0;
  align-self: flex-start;
  margin-right: auto;
}

/* Form Styling */
form {
  display: flex;
  padding: 16px;
  background: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  gap: 12px;
}

textarea {
  flex-grow: 1;
  border: none;
  border-radius: 14px;
  padding: 14px 18px;
  font-size: 0.95rem;
  resize: none;
  outline: none;
  background: rgba(51, 65, 85, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #f1f5f9;
  font-family: inherit;
  transition: all 0.3s ease;
  border: 1px solid rgba(148, 163, 184, 0.2);
  line-height: 1.5;
}

textarea:focus {
  background: rgba(51, 65, 85, 0.8);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

textarea::placeholder {
  color: rgba(203, 213, 225, 0.5);
}

button.send {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.9), rgba(14, 165, 233, 0.9));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: none;
  border-radius: 14px;
  color: white;
  font-weight: 600;
  padding: 14px 28px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.95rem;
  border: 1px solid rgba(6, 182, 212, 0.3);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

button.send:hover {
  background: linear-gradient(135deg, rgba(6, 182, 212, 1), rgba(14, 165, 233, 1));
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
}

button.send:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.4);
}

audio {
  display: none;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  body {
    height: 100vh;
    height: 100dvh;
  }

  .sidebar {
    width: 260px;
    left: -260px;
  }

  .sidebar:hover {
    left: 0;
  }

  .chat-container {
    margin-left: 0;
    width: 100%;
    height: 100vh;
    height: 100dvh;
  }

  .chat-box {
    padding: 12px;
    padding-bottom: 80px;
  }

  .msg {
    max-width: 85%;
    font-size: 0.9rem;
    padding: 12px 14px;
  }

  form {
    padding: 10px;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(30, 41, 59, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
  }

  textarea {
    font-size: 0.9rem;
    padding: 12px 14px;
  }

  button.send {
    padding: 12px 20px;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .msg {
    max-width: 90%;
  }

  .sidebar h2 {
    font-size: 1.5rem;
  }
}
</style>
</head>
<body>

<div class="sidebar" id="sidebar">
  <h2>Orion AI</h2>
  <button id="newChat">+ Percakapan Baru</button>
  <div id="historyList" style="flex-grow:1; overflow-y:auto; margin-top:10px;"></div>
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
const music = document.getElementById('bgMusic');

const sidebar = document.getElementById('sidebar');

let currentChatId = Date.now();
let chats = JSON.parse(localStorage.getItem('chats')||'{}');
if(!chats[currentChatId]) chats[currentChatId]=[];

function saveChats(){ localStorage.setItem('chats', JSON.stringify(chats)); }
function formatText(text){ return text.replace(/\\n/g,"<br>"); }

function renderChat(){
    chat.innerHTML = '';
    for(const msg of chats[currentChatId]){
        const div=document.createElement('div');
        div.className='msg '+msg.sender;
        div.innerHTML=formatText(msg.text);
        chat.appendChild(div);
    }
    chat.scrollTop=chat.scrollHeight;
}

function renderHistory(){
    historyList.innerHTML='';
    Object.keys(chats).sort((a,b)=>a-b).forEach(id=>{
        let firstMsg = 'Percakapan baru';
        if(chats[id][0] && chats[id][0].text){
            firstMsg = chats[id][0].text.length>25 ? chats[id][0].text.slice(0,25)+'...' : chats[id][0].text;
        }
        const btn=document.createElement('button');
        btn.innerText = firstMsg;
        btn.onclick=()=>{ currentChatId=id; renderChat(); };
        historyList.appendChild(btn);
    });
}

newChatBtn.onclick = ()=>{
    currentChatId = Date.now();
    chats[currentChatId]=[];
    saveChats();
    renderChat();
    renderHistory();
};

// Munculkan sidebar ketika kursor dekat pinggir kiri
document.body.addEventListener('mousemove', e=>{
    if(e.clientX <= 20){
        sidebar.style.left = '0';
    } else if(!sidebar.matches(':hover')){
        sidebar.style.left = '-280px';
    }
});

// Untuk mobile, klik di pinggir kiri untuk muncul
document.body.addEventListener('touchstart', e=>{
    if(e.touches[0].clientX <= 20){
        sidebar.style.left = '0';
    }
});

form.addEventListener('submit',async e=>{
    e.preventDefault();
    const question = input.value.trim();
    if(!question) return;
    chats[currentChatId].push({sender:'user', text:question});
    saveChats();
    renderChat();
    renderHistory();
    input.value='';
    const loader={sender:'ai', text:'...'};
    chats[currentChatId].push(loader);
    renderChat();

    const res = await fetch('/ask',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({question})
    });
    const data = await res.json();
    chats[currentChatId].pop();
    chats[currentChatId].push({sender:'ai', text:data.answer||'⚠️ Terjadi kesalahan.'});
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
            for title,link in items[1:5]: news.append(f"📰 {title}\\n🔗 {link}")
            return "\\n\\n".join(news)
        return "Tidak ada berita terbaru ditemukan."
    except Exception as e:
        return f"❌ Gagal ambil berita: {str(e)}"

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
        data=response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer":f"❌ Error: {str(e)}"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)

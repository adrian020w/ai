#!/bin/bash
set -e
echo "🚀 Menyiapkan Orion AI (Flask + Cloudflare Tunnel)..."

# === Configurable ===
WORKDIR="$(pwd)"
TUNNEL_NAME="orionai"
SUBDOMAIN="orionai.trycloudflare.com"
CLOUDFLARED="$WORKDIR/cloudflared"
API_KEY="PASTE_API_KEY_MU_DI_SINI"

# === Install paket minimal ===
echo "📦 Memperbarui & memasang paket..."
pkg update -y || true
pkg upgrade -y || true
pkg install -y python git wget curl || true

# === Install Python libraries ===
echo "📚 Menginstal paket Python..."
pip install --upgrade pip || true
pip install flask requests || true

# === Buat app.py jika belum ada ===
if [ ! -f "$WORKDIR/app.py" ]; then
cat > "$WORKDIR/app.py" <<PY
from flask import Flask, request, jsonify, render_template_string
import requests, re

app = Flask(__name__)

API_KEY = "$API_KEY"
AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

html = """<!DOCTYPE html>
<!-- Paste semua HTML/JS/CSS frontend Orion AI mu di sini -->
</html>
"""

def get_latest_news(query):
    try:
        url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=id&gl=ID&ceid=ID:id"
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return "Gagal mengambil berita terbaru."
        items = re.findall(r"<title>(.*?)</title>", r.text)
        links = re.findall(r"<link>(.*?)</link>", r.text)
        news_list=[]
        for t,l in zip(items[1:5], links[1:5]):
            news_list.append(f"📰 {t}\\n🔗 {l}")
        return "\\n\\n".join(news_list) if news_list else "Tidak ada berita terbaru."
    except Exception as e:
        return f"❌ Gagal ambil berita: {str(e)}"

@app.route("/")
def home():
    return render_template_string(html)

@app.route("/ask", methods=["POST"])
def ask():
    data=request.json
    question = data.get("question","").strip()
    if not question: return jsonify({"answer":"⚠️ Masukkan pertanyaan."})
    try:
        if "berita" in question.lower() or "news" in question.lower():
            topic = re.sub(r"berita|terbaru|news","", question, flags=re.I).strip()
            return jsonify({"answer": get_latest_news(topic if topic else "Indonesia")})
        payload={"contents":[{"parts":[{"text": question}]}]}
        resp=requests.post(AI_URL,json=payload,timeout=10)
        resp.raise_for_status()
        data=resp.json()
        answer = data.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","⚠️ Tidak ada jawaban")
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"❌ Error: {str(e)}"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
PY
echo "✅ app.py dibuat."
fi

# === Hentikan Flask lama jika ada ===
echo "🛑 Menghentikan Flask lama..."
pkill -f "python app.py" 2>/dev/null || echo "✅ Tidak ada server lama"

# === Jalankan Flask di background ===
echo "🧠 Menjalankan Flask..."
nohup python app.py > "$WORKDIR/log.txt" 2>&1 &
sleep 3
echo "✅ Flask berjalan. Log: $WORKDIR/log.txt"

# === Download cloudflared jika belum ada ===
if [ ! -x "$CLOUDFLARED" ]; then
  echo "⬇️ Mengunduh cloudflared ARM64..."
  wget -q --show-progress https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O cloudflared
  chmod +x cloudflared
  CLOUDFLARED="$WORKDIR/cloudflared"
  echo "✅ cloudflared siap."
fi

# === Jalankan tunnel trycloudflare (subdomain gratis) ===
echo "🌐 Menjalankan Cloudflare Tunnel..."
nohup "$CLOUDFLARED" tunnel --url http://localhost:5000 --hostname "$SUBDOMAIN" > "$WORKDIR/cloudflared.log" 2>&1 &
sleep 4

echo "✅ Tunnel aktif. Akses Orion AI di:"
echo "➡️ https://$SUBDOMAIN"
echo "📄 Cek log cloudflared: $WORKDIR/cloudflared.log"
echo "📄 Cek log Flask: $WORKDIR/log.txt"

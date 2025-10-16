#!/bin/bash
set -euo pipefail

echo "🚀 Menyiapkan Orion AI (Flask + Cloudflare Tunnel)..."

# =========================
# Configurable
# =========================
WORKDIR="/root/cloudflare"
TUNNEL_NAME="orionai"
SUBDOMAIN="orionai.trycloudflare.com"
TID="d4153116-9a7e-4f91-a06c-b5aac97809ba"

CLOUDFLARED_BIN="/root/cloudflared/cloudflared"  # sesuaikan lokasi binary

mkdir -p "$WORKDIR"
mkdir -p "$HOME/.cloudflared"

# =========================
# Pastikan Flask app ada
# =========================
APP="$WORKDIR/app.py"
if [ ! -f "$APP" ]; then
cat > "$APP" <<PY
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Halo! Orion AI (Flask) berjalan via Cloudflare Tunnel 😎"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
PY
    echo "✅ Contoh app.py dibuat."
fi

# =========================
# Jalankan Flask di background
# =========================
echo "🧠 Menjalankan Flask di background..."
nohup python "$APP" > "$WORKDIR/log_flask.txt" 2>&1 &
sleep 2
echo "✅ Flask dijalankan. Log: $WORKDIR/log_flask.txt"

# =========================
# Buat config.yml untuk tunnel
# =========================
CONFIG_FILE="$WORKDIR/config.yml"
cat > "$CONFIG_FILE" <<YML
tunnel: $TID
credentials-file: $HOME/.cloudflared/$TID.json

ingress:
  - hostname: $SUBDOMAIN
    service: http://localhost:5000
  - service: http_status:404
YML
echo "✅ config.yml dibuat di $CONFIG_FILE"

# =========================
# Cek credentials JSON
# =========================
CREDS_FILE="$HOME/.cloudflared/$TID.json"
if [ ! -f "$CREDS_FILE" ]; then
    echo "❌ File credentials JSON tidak ditemukan: $CREDS_FILE"
    echo "Pastikan sudah menjalankan cloudflared login & tunnel create $TID"
    exit 1
fi
echo "✅ File credentials JSON ditemukan: $CREDS_FILE"

# =========================
# Jalankan tunnel
# =========================
echo "🌐 Menjalankan Cloudflare Tunnel..."
nohup "$CLOUDFLARED_BIN" tunnel --config "$CONFIG_FILE" run "$TUNNEL_NAME" > "$WORKDIR/log_cloudflared.txt" 2>&1 &
sleep 4

echo "✅ Tunnel dijalankan. Log: $WORKDIR/log_cloudflared.txt"
echo ""
echo "🔗 Akses Orion AI via: https://$SUBDOMAIN"
echo "📝 Cek log Flask: tail -f $WORKDIR/log_flask.txt"
echo "📝 Cek log Tunnel: tail -f $WORKDIR/log_cloudflared.txt"

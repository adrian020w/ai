#!/bin/bash
set -e
echo "🚀 Menyiapkan lingkungan AI Chat Adrian..."

# === Update & Install Paket ===
echo "📦 Memperbarui paket & menginstal dependency..."
pkg update -y || true
pkg upgrade -y || true
pkg install -y python git wget || true

# === Install Library Python ===
echo "📚 Menginstal library Python..."
pip install --upgrade pip || true
pip install flask requests || true

# Working dir (asumsi kamu menjalankan skrip ini di ~/ai)
WORKDIR="$(pwd)"
echo "ℹ️ Working directory: $WORKDIR"

# === Hentikan proses Flask sebelumnya jika ada ===
echo "🛑 Menghentikan server Flask lama jika ada..."
pkill -f "python app.py" 2>/dev/null || echo "✅ Tidak ada server lama yang berjalan"

# === Pastikan app.py ada (jika tidak, buat contoh minimal) ===
if [ ! -f "$WORKDIR/app.py" ]; then
  echo "⚠️ app.py tidak ditemukan — membuat contoh app.py..."
  cat > "$WORKDIR/app.py" <<'PY'
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Halo! Flask di HP via Cloudflare Tunnel 😎"
if __name__ == "__main__":
    app.run(port=5000)
PY
  echo "✅ Contoh app.py dibuat."
fi

# === Jalankan Flask Server di background ===
echo "🧠 Menjalankan server Flask di background..."
nohup python app.py > "$WORKDIR/log.txt" 2>&1 &
sleep 3
echo "✅ Flask server berjalan di background. Log disimpan di $WORKDIR/log.txt"

# === Temukan atau download cloudflared ===
TUNNEL_NAME="myflask"
SUBDOMAIN="myflask.trycloudflare.com"
CLOUDFLARED_PATHS=(
  "$WORKDIR/cloudflared"
  "$HOME/cloudflared"
  "$HOME/.cffolder/cloudflared"
  "$HOME/CamPhish/CamPhish/cloudflared"
  "$HOME/bin/cloudflared"
  "/data/data/com.termux/files/home/cloudflared"
  "/data/data/com.termux/files/home/.cffolder/cloudflared"
)
FOUND=""
echo "🔎 Mencari binary cloudflared di lokasi umum..."
for p in "${CLOUDFLARED_PATHS[@]}"; do
  if [ -x "$p" ]; then
    FOUND="$p"
    break
  fi
  if [ -f "$p" ]; then
    chmod +x "$p" 2>/dev/null || true
    if [ -x "$p" ]; then
      FOUND="$p"
      break
    fi
  fi
done

# juga coba cari dengan find sebagai fallback (cari di home)
if [ -z "$FOUND" ]; then
  echo "⚙️ Fallback: mencari file cloudflared di HOME..."
  hit=$(find "$HOME" -maxdepth 4 -type f -iname 'cloudflared*' 2>/dev/null | head -n 1 || true)
  if [ -n "$hit" ]; then
    chmod +x "$hit" 2>/dev/null || true
    FOUND="$hit"
  fi
fi

# kalau belum ditemukan, download ARM64 ke working dir
if [ -z "$FOUND" ]; then
  echo "⬇️ cloudflared tidak ditemukan — mengunduh versi ARM64 ke $WORKDIR/cloudflared ..."
  cd "$WORKDIR"
  if wget -q --show-progress https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O cloudflared; then
    chmod +x cloudflared
    FOUND="$WORKDIR/cloudflared"
    echo "✅ cloudflared diunduh dan siap."
  else
    echo "❌ Gagal mengunduh cloudflared otomatis. Silakan download manual dan letakkan file bernama 'cloudflared' di $WORKDIR"
    exit 1
  fi
fi

CLOUDFLARED="$FOUND"
echo "✅ Menggunakan cloudflared: $CLOUDFLARED"

# Tampilkan versi (informasi)
echo "ℹ️ cloudflared version:"
"$CLOUDFLARED" --version || true

# === Jalankan Cloudflare Tunnel ===
echo "🌐 Menjalankan Cloudflare Tunnel..."
# Jika ada config.yml di working dir, gunakan itu
if [ -f "$WORKDIR/config.yml" ]; then
  nohup "$CLOUDFLARED" tunnel --config "$WORKDIR/config.yml" run "$TUNNEL_NAME" > "$WORKDIR/cloudflared.log" 2>&1 &
  sleep 3
  echo "✅ Cloudflare Tunnel berjalan (via config.yml). Log: $WORKDIR/cloudflared.log"
  echo "➡️ Link publik permanen: https://$SUBDOMAIN"
else
  # Cek apakah sudah login / ada kredensial di ~/.cloudflared
  if [ -d "$HOME/.cloudflared" ] && ls "$HOME/.cloudflared"/*.json >/dev/null 2>&1; then
    echo "ℹ️ Menemukan kredensial Cloudflare di ~/.cloudflared. Menjalankan tunnel dengan nama $TUNNEL_NAME..."
    nohup "$CLOUDFLARED" tunnel run "$TUNNEL_NAME" > "$WORKDIR/cloudflared.log" 2>&1 &
    sleep 3
    echo "✅ Cloudflare Tunnel berjalan (menggunakan kredensial di ~/.cloudflared). Log: $WORKDIR/cloudflared.log"
    echo "➡️ Link publik (cek config/hostname yang kamu daftarkan saat buat tunnel)."
  else
    echo "⚠️ Belum ada config.yml dan belum login ke Cloudflare dari cloudflared."
    echo "➡️ Jika ini pertama kali: jalankan manual:"
    echo "   $CLOUDFLARED login"
    echo "   # lalu buat tunnel dan catat TUNNEL_ID:"
    echo "   $CLOUDFLARED tunnel create $TUNNEL_NAME"
    echo "   # lalu buat config.yml seperti di README agar hostname auto-bind"
    echo ""
    echo "Skrip selesai — cloudflared sudah tersedia di: $CLOUDFLARED"
  fi
fi

echo "Selesai."

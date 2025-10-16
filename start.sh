cd ~/ai
cat > start.sh <<'SH'
#!/bin/bash
set -e
echo "🚀 Menyiapkan lingkungan Orion AI (Flask + Cloudflare Tunnel)..."

# === Configurable ===
WORKDIR="$(pwd)"
TUNNEL_NAME="orionai"
SUBDOMAIN="orionai.trycloudflare.com"
CLOUDFLARED_CANDIDATES=(
  "$WORKDIR/cloudflared"
  "$HOME/cloudflared"
  "$HOME/.cffolder/cloudflared"
  "$HOME/CamPhish/CamPhish/cloudflared"
  "$HOME/bin/cloudflared"
  "/data/data/com.termux/files/home/cloudflared"
  "/data/data/com.termux/files/home/.cffolder/cloudflared"
)

echo "ℹ️ Workdir: $WORKDIR"
echo "ℹ️ Nama tunnel: $TUNNEL_NAME"
echo "ℹ️ Subdomain yang diinginkan: https://$SUBDOMAIN"
echo ""

# === Update & Install minimal packages ===
echo "📦 Memperbarui & memasang paket yang diperlukan..."
pkg update -y || true
pkg upgrade -y || true
pkg install -y python git wget curl || true

# === Python packages ===
echo "📚 Menginstal paket Python (flask, requests)..."
pip install --upgrade pip || true
pip install flask requests || true

# === Pastikan app.py ada dan bind ke 0.0.0.0 ===
if [ ! -f "$WORKDIR/app.py" ]; then
  echo "⚠️ app.py tidak ditemukan. Membuat contoh app.py yang bind ke 0.0.0.0..."
  cat > "$WORKDIR/app.py" <<'PY'
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Halo! Orion AI (Flask) berjalan via Cloudflare Tunnel 😎"
if __name__ == "__main__":
    # bind ke 0.0.0.0 supaya bisa diakses oleh cloudflared dari localhost
    app.run(host='0.0.0.0', port=5000)
PY
  echo "✅ Contoh app.py dibuat."
fi

# === Hentikan Flask lama ===
echo "🛑 Menghentikan server Flask lama jika ada..."
pkill -f "python app.py" 2>/dev/null || echo "✅ Tidak ada server Flask lama berjalan"

# === Jalankan Flask di background (log ke file) ===
echo "🧠 Menjalankan Flask di background..."
nohup python app.py > "$WORKDIR/log.txt" 2>&1 &
sleep 2
echo "✅ Flask dijalankan. Cek lokal: http://127.0.0.1:5000"
echo "   (Log: $WORKDIR/log.txt)"
echo ""

# === Uji akses lokal supaya tahu apakah Flask memang berjalan ===
echo "🔎 Mengecek endpoint lokal..."
if curl -sS --max-time 3 http://127.0.0.1:5000 >/dev/null 2>&1; then
  echo "✅ Flask merespons di http://127.0.0.1:5000"
else
  echo "❌ Flask tidak merespons di 127.0.0.1:5000 — cek $WORKDIR/log.txt"
  echo "   Tampilkan 20 baris terakhir log:"
  tail -n 20 "$WORKDIR/log.txt" || true
  echo "   Jika error terkait binding atau modul hilang, perbaiki app.py atau pip install modul yang diperlukan."
  # kita tidak exit karena mungkin cloudflared bisa show error nanti
fi
echo ""

# === Cari atau download cloudflared ===
FOUND=""
echo "🔎 Mencari binary cloudflared di lokasi umum..."
for p in "${CLOUDFLARED_CANDIDATES[@]}"; do
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

# fallback find
if [ -z "$FOUND" ]; then
  hit=$(find "$HOME" -maxdepth 4 -type f -iname 'cloudflared*' 2>/dev/null | head -n 1 || true)
  if [ -n "$hit" ]; then
    chmod +x "$hit" 2>/dev/null || true
    FOUND="$hit"
  fi
fi

# download jika belum ada
if [ -z "$FOUND" ]; then
  echo "⬇️ cloudflared tidak ditemukan — mengunduh versi ARM64 ke $WORKDIR/cloudflared ..."
  cd "$WORKDIR"
  if wget -q --show-progress https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O cloudflared; then
    chmod +x cloudflared
    FOUND="$WORKDIR/cloudflared"
    echo "✅ cloudflared diunduh ke $FOUND"
  else
    echo "❌ Gagal mengunduh cloudflared otomatis. Silakan download manual dan letakkan file bernama 'cloudflared' di $WORKDIR"
    exit 1
  fi
fi

CLOUDFLARED="$FOUND"
echo "✅ Menggunakan cloudflared: $CLOUDFLARED"
echo "ℹ️ Versi:"
"$CLOUDFLARED" --version || true
echo ""

# === Pastikan user login & tunnel dibuat; kalau belum, instruksi manual interaktif ===
# Cek kredensial
if [ -d "$HOME/.cloudflared" ] && ls "$HOME/.cloudflared"/*.json >/dev/null 2>&1; then
  echo "ℹ️ Kredensial Cloudflare ditemukan di ~/.cloudflared."
else
  echo "⚠️ Belum ada kredensial Cloudflare (belum login). Kamu harus login sekali."
  echo "➡️ Perintah yang harus kamu jalankan sekarang (akan membuka browser):"
  echo "   $CLOUDFLARED login"
  echo ""
  echo "Setelah login, jalankan:"
  echo "   $CLOUDFLARED tunnel create $TUNNEL_NAME"
  echo "Catat TUNNEL_ID yang dihasilkan, lalu jalankan skrip ini lagi."
  echo "Skrip akan berhenti sekarang supaya kamu bisa login."
  exit 0
fi

# === Jika tunnel belum dibuat, buat otomatis ===
# Cek apakah sudah ada tunnel dengan nama TUNNEL_NAME
if "$CLOUDFLARED" tunnel list 2>/dev/null | grep -q -i "$TUNNEL_NAME"; then
  echo "ℹ️ Tunnel bernama $TUNNEL_NAME sudah ada."
else
  echo "⬆️ Tunnel $TUNNEL_NAME belum ada — akan dibuat otomatis (interaktif)..."
  "$CLOUDFLARED" tunnel create "$TUNNEL_NAME" || {
    echo "❌ Gagal membuat tunnel secara otomatis. Jalankan manual:"
    echo "   $CLOUDFLARED tunnel create $TUNNEL_NAME"
    exit 1
  }
  echo "✅ Tunnel $TUNNEL_NAME dibuat."
fi

# Ambil TUNNEL_ID (ambil yang pertama yang cocok)
T_ID=$("$CLOUDFLARED" tunnel list --output json 2>/dev/null | grep -oP '"id":"\K[^"]+' | head -n1 || true)
if [ -z "$T_ID" ]; then
  # fallback parse from tunnel list text
  T_ID=$("$CLOUDFLARED" tunnel list 2>/dev/null | awk '/'"$TUNNEL_NAME"'/ {print $1; exit}' || true)
fi

echo "ℹ️ Tunnel ID (kira-kira): $T_ID"

# === Buat config.yml di ~/.cloudflared jika belum ada ===
CFG="$WORKDIR/config.yml"
if [ ! -f "$CFG" ]; then
  echo "🔧 Membuat config.yml contoh di $CFG ..."
  mkdir -p "$HOME/.cloudflared"
  cat > "$CFG" <<YML
tunnel: $T_ID
credentials-file: $HOME/.cloudflared/$T_ID.json

ingress:
  - hostname: $SUBDOMAIN
    service: http://localhost:5000
  - service: http_status:404
YML
  echo "✅ config.yml dibuat. (Isi: hostname -> $SUBDOMAIN)"
else
  echo "ℹ️ config.yml sudah ada: $CFG"
fi

# === Jalankan tunnel menggunakan config.yml ===
echo "🌐 Menjalankan Cloudflare Tunnel (run $TUNNEL_NAME) ..."
nohup "$CLOUDFLARED" tunnel --config "$CFG" run "$TUNNEL_NAME" > "$WORKDIR/cloudflared.log" 2>&1 &
sleep 4

# === Cek apakah tunnel aktif dengan memperhatikan log ===
echo "🔍 Mengecek log cloudflared (20 baris terakhir) — tunggu beberapa detik..."
sleep 2
tail -n 20 "$WORKDIR/cloudflared.log" || true

echo ""
echo "✅ Perintah dijalankan. Bila semuanya sukses, akses:"
echo "   https://$SUBDOMAIN"
echo ""
echo "Jika situs masih 'tidak dapat dijangkau', lakukan pengecekan berikut:"

cat <<'DOC'

1) Cek respon lokal:
   curl -v http://127.0.0.1:5000

   - Kalau tidak ada respon: buka log.txt (Flask) dan perbaiki app.py.
     tail -n 40 log.txt

2) Cek log cloudflared:
   tail -n 200 cloudflared.log
   - Cari kata 'ERROR' atau 'FAILED' atau 'listen' atau 'certificate'.

3) Pastikan kamu sudah login & tunnel terdaftar:
   cloudflared login
   cloudflared tunnel list
   cloudflared tunnel run <nama>

4) Jika ada pesan 'hostname not found' atau 'ingress' errors:
   - Pastikan saat membuat tunnel kamu mencatat TUNNEL_ID dan config.yml menunjuk ke TUNNEL_ID itu.
   - Jika perlu, hapus config.yml sementara dan jalankan:
       cloudflared tunnel --url http://localhost:5000
     (ini memberikan subdomain trycloudflare otomatis — cocok untuk tes cepat)

5) Jika semua gagal, kirim output dari:
   tail -n 60 cloudflared.log
   dan hasil:
   curl -v http://127.0.0.1:5000

DOC

echo "Selesai."
SH

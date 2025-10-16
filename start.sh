#!/bin/bash
echo "🚀 Menyiapkan lingkungan AI Chat Adrian..."

# === Update & Install Paket ===
echo "📦 Memperbarui paket & menginstal dependency..."
pkg update -y && pkg upgrade -y
pkg install -y python git wget

# === Install Library Python ===
echo "📚 Menginstal library Python..."
pip install --upgrade pip
pip install flask requests

# === Hentikan proses Flask sebelumnya jika ada ===
echo "🛑 Menghentikan server Flask lama jika ada..."
pkill -f "python app.py" 2>/dev/null || echo "✅ Tidak ada server lama yang berjalan"

# === Jalankan Flask Server di background ===
echo "🧠 Menjalankan server Flask di background..."
nohup python app.py > log.txt 2>&1 &
sleep 3
echo "✅ Flask server berjalan di background. Log disimpan di log.txt"

# === Setup Cloudflare Tunnel ===
TUNNEL_NAME="myflask"
CLOUDFLARED="./cloudflared"  # pastikan cloudflared ada di folder yang sama
SUBDOMAIN="myflask.trycloudflare.com"

echo "🌐 Menjalankan Cloudflare Tunnel..."
# Jalankan tunnel
$CLOUDFLARED tunnel --config config.yml run $TUNNEL_NAME &

sleep 3
echo "✅ Cloudflare Tunnel berjalan."
echo "➡️  Link publik permanen: https://$SUBDOMAIN"

#!/bin/bash
echo "🚀 Menyiapkan lingkungan AI Chat Adrian..."

# === Update & Install Paket ===
echo "📦 Memperbarui paket & menginstal dependency..."
pkg update -y && pkg upgrade -y
pkg install -y python openssh git

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

# === Jalankan Serveo untuk akses publik ===
SUBDOMAIN="aiadrian"
echo "🌐 Membuka akses publik melalui Serveo..."
echo "➡️  Link publik: https://$SUBDOMAIN.serveo.net"

# Jalankan koneksi Serveo
# -R = remote forwarding, StrictHostKeyChecking=no agar tidak tanya fingerprint
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -R $SUBDOMAIN:80:localhost:5000 serveo.net

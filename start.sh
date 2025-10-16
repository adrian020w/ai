#!/bin/bash
echo "🚀 Menyiapkan lingkungan AI Chat Adrian..."

# === Update & Install Paket ===
echo "📦 Memperbarui paket..."
pkg update -y && pkg upgrade -y
pkg install -y python openssh git

# === Install Library Python ===
echo "📚 Menginstal library Python..."
pip install --upgrade pip
pip install flask google-genai

# === Jalankan Flask Server ===
echo "🧠 Menjalankan server Flask di background..."

# Hentikan proses Flask sebelumnya jika masih berjalan
pkill -f "python app.py" 2>/dev/null

# Jalankan ulang Flask server di background
nohup python app.py > log.txt 2>&1 &

# Tunggu agar server siap
sleep 3

# === Jalankan Serveo ===
# Ganti 'aiadrian' di bawah dengan subdomain Serveo yang kamu mau, misal 'adrianai'
SUBDOMAIN="aiadrian"

echo "🌐 Membuka akses publik melalui Serveo..."
echo "Gunakan link di bawah ini untuk mengakses web AI kamu:"
echo "➡️  https://$SUBDOMAIN.serveo.net"

# Jalankan Serveo dan arahkan ke port Flask
ssh -o StrictHostKeyChecking=no -R $SUBDOMAIN:80:localhost:5000 serveo.net

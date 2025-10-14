#!/bin/bash
echo "🚀 Menyiapkan lingkungan AI Chat..."

# Update sistem
sudo apt update -y
sudo apt install -y python3 python3-pip git openssh

# Buat virtual env jika belum ada
if [ ! -d "ai_env" ]; then
  python3 -m venv ai_env
fi
source ai_env/bin/activate

# Install library
echo "📚 Menginstal library Python..."
pip install --upgrade pip
pip install flask transformers torch sentencepiece

# Jalankan Flask di background
echo "🧠 Menjalankan server Flask..."
nohup python3 app.py > log.txt 2>&1 &

# Jalankan Serveo
echo "🌐 Membuka port publik..."
ssh -o StrictHostKeyChecking=no -R 80:localhost:5000 serveo.net

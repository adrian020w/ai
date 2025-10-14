#!/bin/bash
# start.sh : aktifkan venv lalu jalankan app.py, kemudian buat tunnel serveo
set -e

# pastikan berada di folder ~ /ai
cd "$(dirname "$0")"

# aktifkan venv jika ada
if [ -f "venv/bin/activate" ]; then
  echo "[INFO] activating venv"
  source venv/bin/activate
else
  echo "[WARN] venv not found. Create one with: python -m venv venv"
fi

# jalankan flask di background
echo "[INFO] starting flask app"
python app.py &

FLASK_PID=$!
sleep 2

echo "[INFO] starting serveo (ssh -R 80:localhost:5000 serveo.net)"
# Jika kamu ingin subdomain tertentu, gunakan -R 80:localhost:5000:subdomain=namamu
ssh -o ServerAliveInterval=60 -R 80:localhost:5000 serveo.net

# jika serveo exit, hentikan flask
kill $FLASK_PID || true

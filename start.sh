#!/bin/bash
echo "Menjalankan Yan AI by Adrian..."

# Jalankan Flask di background
python app.py &
FLASK_PID=$!

# Jalankan Serveo untuk akses publik
ssh -R 80:localhost:5000 serveo.net &
SERVEO_PID=$!

trap "echo 'Menutup Yan AI...'; kill $FLASK_PID $SERVEO_PID" INT

wait
echo "Yan AI telah ditutup."
#!/bin/bash
set -euo pipefail

echo "🚀 Menyiapkan Orion AI (Flask) di Replit..."

# =========================
# Configurable
# =========================
FLASK_APP="${FLASK_APP:-main.py}"   # pastikan main.py ada
PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-3000}"                # Replit otomatis set $PORT

# =========================
# Pastikan Flask app ada
# =========================
if [ ! -f "$FLASK_APP" ]; then
  cat > "$FLASK_APP" <<PY
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Halo! Orion AI (Flask) berjalan di Replit 😎"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
PY
  echo "✅ Contoh main.py dibuat."
else
  echo "✅ Ditemukan Flask app: $FLASK_APP"
fi

# =========================
# Install requirements
# =========================
if [ -f "requirements.txt" ]; then
  echo "📦 Menginstall requirements..."
  $PYTHON_BIN -m pip install -r requirements.txt
fi

# =========================
# Jalankan Flask
# =========================
echo "🧠 Menjalankan Flask di port $PORT..."
nohup $PYTHON_BIN "$FLASK_APP" > log_flask.txt 2>&1 &

sleep 2
echo "✅ Flask dijalankan. Log: log_flask.txt"
echo "🔗 Akses Orion AI via: https://$REPL_SLUG.$REPL_OWNER.repl.co (otomatis Replit)"
echo "📝 Cek log Flask: tail -f log_flask.txt"

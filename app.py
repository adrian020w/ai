# app.py
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# Try to load BlenderBot model (may fail on Termux aarch64 if torch wheel not available)
MODEL_NAME = "facebook/blenderbot-400M-distill"
use_local_model = True
model = None
tokenizer = None

try:
    # import here to catch errors gracefully
    from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
    import torch

    # Force CPU (if torch installed)
    device = torch.device("cpu")
    tokenizer = BlenderbotTokenizer.from_pretrained(MODEL_NAME)
    model = BlenderbotForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.to(device)

    print("[INFO] Local BlenderBot model loaded (CPU).")
except Exception as e:
    use_local_model = False
    print("[WARN] Failed to load local model:", e)
    print("[WARN] The app will use a lightweight fallback responder.")

# Simple fallback responder (very basic, but will always work)
def fallback_respond(prompt: str) -> str:
    # very simple heuristics + canned reply to help with 'homework-like' queries
    low = prompt.lower()
    if any(word in low for word in ["jelaskan", "definisi", "apa itu", "pengertian", "definisi dari"]):
        return "Berikut penjelasan singkat: " + prompt + " — (maaf, mode fallback: jawaban ringkas; jalankan model lokal untuk jawaban lebih lengkap)."
    if any(word in low for word in ["buatkan", "ringkas", "ringkasan", "resume", "summarize"]):
        return "Ringkasan: (mode fallback) " + " ".join(low.split()[:40]) + "..."
    # default echo + suggestion
    return "Maaf, saya belum bisa menjawab panjang karena model lokal belum ada. Coba jalankan di server yang mendukung PyTorch CPU/GPU.\n\nKamu menulis: " + prompt

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Masukkan teks terlebih dahulu"}), 400

    if use_local_model and model is not None and tokenizer is not None:
        try:
            # use CPU and generate a response
            inputs = tokenizer(text, return_tensors="pt")
            reply_ids = model.generate(**inputs, max_length=200, num_beams=4, early_stopping=True)
            reply = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
            return jsonify({"reply": reply})
        except Exception as e:
            # fall back on error
            print("[ERROR] generation failed:", e)

    # fallback responder when local model not available
    return jsonify({"reply": fallback_respond(text)})

if __name__ == "__main__":
    # host 0.0.0.0 so Serveo or SSH tunnel can forward
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

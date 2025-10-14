from flask import Flask, render_template, request, jsonify
from transformers import pipeline

app = Flask(__name__)

print("🧠 Memuat model AI (Flan-T5 Base)...")
ai = pipeline("text2text-generation", model="google/flan-t5-base")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"reply": "Ketik dulu pertanyaannya ya 😄"})
    
    print(f"🗨️  Pertanyaan: {text}")
    result = ai(text, max_length=400)
    return jsonify({"reply": result[0]["generated_text"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

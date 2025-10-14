from flask import Flask, render_template, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Gunakan model open-source yang sudah terlatih penuh
# (Kecil dan cocok untuk HP)
generator = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")

    # AI menjawab otomatis
    result = generator(question, max_new_tokens=150, temperature=0.7)
    answer = result[0]["generated_text"]

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

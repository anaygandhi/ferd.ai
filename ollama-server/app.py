from flask import Flask, request, jsonify
import os
import requests
import yaml

app = Flask(__name__)

# Load config.yaml if needed (optional)
with open("run.yaml", "r") as f:
    config = yaml.safe_load(f)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_ID = os.getenv("INFERENCE_MODEL", "llama3.2:1b-instruct-fp16")


@app.route("/")
def index():
    return jsonify({"status": "OK", "model": MODEL_ID})


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    payload = {
        "model": MODEL_ID,
        "prompt": prompt,
        "stream": False
    }

    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
        res.raise_for_status()
        return jsonify(res.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8321)

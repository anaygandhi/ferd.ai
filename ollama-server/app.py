from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import yaml

app = Flask(__name__)
CORS(app)

# Load config.yaml if needed (optional)
with open("run.yaml", "r") as f:
    config = yaml.safe_load(f)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_ID = os.getenv("INFERENCE_MODEL", "llama3.2:1b-instruct-fp16")
BASE_DIR = os.getcwd()


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
        return jsonify({"error": f"Request to OLLAMA failed: {str(e)}"}), 500

@app.route("/list_files", methods=["GET"])
@app.route("/list-files", methods=["GET"])
def list_files():
    directory = "/"
    try:
        files = os.listdir(directory)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/read_file", methods=["POST"])
def read_file():
    """ Read the contents of a specific file and return the first 200 words as readable text """
    data = request.get_json()
    file_name = data.get("file_name")

    if not file_name:
        return jsonify({"error": "No file name provided"}), 400

    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        words = content.split()
        first_200_words = ' '.join(words[:200])

        return jsonify({"file_name": file_name, "content": first_200_words})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ai-assistant", methods=["POST"])
def ai_assistant():
    """Endpoint for AI assistant to interact with the server"""
    data = request.get_json()
    action = data.get("action")
    params = data.get("params", {})

    if not action:
        return jsonify({"error": "No action specified"}), 400

    if action == "generate":
        prompt = params.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided for generate action"}), 400

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
            return jsonify({"error": f"Request to OLLAMA failed: {str(e)}"}), 500

    elif action == "list_files":
        directory = params.get("directory", "/")
        try:
            files = os.listdir(directory)
            return jsonify({"files": files})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif action == "read_file":
        file_name = params.get("file_name")
        if not file_name:
            return jsonify({"error": "No file name provided"}), 400

        file_path = os.path.join(BASE_DIR, file_name)

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            words = content.split()
            first_200_words = ' '.join(words[:200])

            return jsonify({"file_name": file_name, "content": first_200_words})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": f"Unknown action: {action}"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8321)

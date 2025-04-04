from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import os
import yaml
from gevent.pywsgi import WSGIServer

from blueprints import fs_bp, ai_bp


# --- Flask init --- #
app = Flask(__name__)
CORS(app)

# Load config.yaml if needed (optional)
with open("run.yaml", "r") as f:
    config = yaml.safe_load(f)

# Add the config vars to the app so they can be accessed in the blueprints
app.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
app.MODEL_ID = os.getenv("INFERENCE_MODEL", "llama3.2:1b-instruct-fp16")
app.BASE_DIR = os.getcwd()

# Log incoming requests
@app.before_request
def before_request(): 
    print(f'\n\033[94mINCOMING REQUEST: \n\n\033[0m\tMethod: {request.method}\n\tPath: {request.path}\n')
    

# --- Endpoints and Blueprints --- # 
# Index endpoint 
@app.route("/")
def index(): return jsonify({"status": "OK", "model": current_app.MODEL_ID})

# Blueprints
app.register_blueprint(fs_bp)     # Filesystem blueprint
app.register_blueprint(ai_bp)     # AI Assistant blueprint


# --- Run --- #
if __name__ == "__main__":
    print('\033[92mStarting flask server...\033[0m')
    
    # Create and serve the WSGI server
    http_server = WSGIServer(('0.0.0.0', 8321), app)
    http_server.serve_forever()
    
    
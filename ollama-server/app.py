from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import os
import yaml
from gevent.pywsgi import WSGIServer
from configparser import ConfigParser

from blueprints import fs_bp, ai_bp


# --- Flask init --- #
app = Flask(__name__)
CORS(app)

# Load config 
config:ConfigParser = ConfigParser()
config.read('config/config.conf')

# Add the config vars to the app so they can be accessed in the blueprints
app.OLLAMA_URL = config['ollama']['OLLAMA_URL']     # URL for the Ollama model
app.MODEL_ID = config['ollama']['OLLAMA_MODEL']     # Ollama model name
app.EMBEDDING_DIM = int(config['index']['EMBEDDING_DIM'].strip())   # Embedding dim for index
app.INDEX_BIN_PATH = config['paths']['INDEX_BIN_PATH']      # Faiss index binary
app.METADATA_DB_PATH = config['paths']['METADATA_DB_PATH']  # SQLite DB with file metadata
app.K = int(config['index']['K'].strip())                           # Pick top K matched files for querying 

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
    http_server = WSGIServer(('0.0.0.0', int(config['flask']['FLASK_PORT'])), app)
    http_server.serve_forever()
    
    
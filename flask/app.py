"""
app.py

DESC: the main script to run the flask server. 
"""

# Info print
print('\n--------------------------------------------------')
print('\033[94mINFO: \033[0minitializing flask server.\n')

import threading as th 

from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from configparser import ConfigParser
from objects import OllamaQueryHandler, FileMetadataDatabase, FilesystemIndexer
from sentence_transformers import SentenceTransformer

from ollama import ResponseError as OllamaResponseError
from ollama import Client as OllamaClient

from blueprints import fs_bp, ai_bp
from utils import get_root_directories


# --- Flask init --- #
app = Flask(__name__)
CORS(app)

# Load config 
config:ConfigParser = ConfigParser()
config.read('config/config.conf')

# Add the config vars to the app so they can be accessed in the blueprints
app.OLLAMA_URL = config['ollama']['OLLAMA_URL']                     # URL for the Ollama model
app.MODEL_ID = config['ollama']['OLLAMA_MODEL']                     # Ollama model name
app.EMBEDDING_DIM = int(config['index']['EMBEDDING_DIM'].strip())   # Embedding dim for index
app.INDEX_BIN_PATH = config['paths']['INDEX_BIN_PATH']              # Faiss index binary
app.METADATA_DB_PATH = config['paths']['METADATA_DB_PATH']          # SQLite DB with file metadata
app.K = int(config['index']['K'].strip())                           # Pick top K matched files for querying 

# Init a db connection to the file metadata db and add to the app
app.file_metadata_db = FileMetadataDatabase(config['paths']['METADATA_DB_PATH'])

# Init a file indexer and add to the app
app.filesystem_indexer = FilesystemIndexer(
    get_root_directories()[0],                      # start_dir - NOTE: Use the first mounted drive as the default
    config['paths']['METADATA_DB_PATH'],            # metadata_db_path
    config['paths']['INDEX_BIN_PATH'],              # index_bin_path
    int(config['index']['EMBEDDING_DIM'].strip())   # embedding_dim
)

# Init an ollama query handler and add to the app
app.ollama_query_handler = OllamaQueryHandler(
    OllamaClient(host=config['ollama']['OLLAMA_URL']),
    app.MODEL_ID
)

# Init a sentence transformer model and add to the app
app.sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')  


# --- Test the ollama client --- # 
print('\n\033[93mNOTICE: \033[0mtesting Ollama client with question: "What is the capital of France?"')

try: 
    response = app.ollama_query_handler.generate(
        prompt='What is the capital of France?'
    )

    print('\033[93mNOTICE: \033[0mOllama response:', response)

# Handle exceptions
# Ollama response error most likely means the proper model is not pulled
except OllamaResponseError as e: 
    print(f'\033[91mERROR in app.py: \033[0merror when testing Ollama client connection (OllamaResponseError). Is the model pulled (expecting: "{app.MODEL_ID}")?')
    print(e)
    quit()

# Connection error most likely means that the ollama instance is not running
except ConnectionError as e: 
    print(f'\033[91mERROR in app.py: \033[0merror connecting to the Ollama instance. Is it running (expecting URL: "{app.OLLAMA_URL}")?')
    print(e) 
    quit()

# Other exceptions
except Exception as e: 
    print('\033[91mERROR in app.py: \033[0man unknown error occured when testing the Ollama connection.')
    print(e) 
    quit()

# Ollama test complete
print('\033[92mSUCCESS: \033[0mOllama client connected successfully.')


# --- Log incoming requests --- #
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
    
    # Info print
    print(f'\033[92mSUCCESS: \033[0mFlask server running on port {config["flask"]["FLASK_PORT"]}.')
    
    # Create and serve the WSGI server
    http_server = WSGIServer(('0.0.0.0', int(config['flask']['FLASK_PORT'])), app)
    http_server.serve_forever()
    
    
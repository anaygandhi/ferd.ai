from flask import Blueprint, jsonify, request, current_app 
import requests 
import os 
from utils import get_root_directories
import platform 


# --- Config --- #
# Init blueprint
fs_bp:Blueprint = Blueprint('fs_bp', __name__)


# --- Endpoints --- # 

@fs_bp.route("/list-files", methods=["GET"])
def list_files():
    """ Lists the files in the root directory """
    
    directory = "/"
    try:
        files = os.listdir(directory)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fs_bp.route("/read_file", methods=["POST"])
def read_file():
    """ Read the contents of a specific file and return the first 200 words as readable text """
    
    data = request.get_json()
    file_name = data.get("file_name")

    if not file_name:
        return jsonify({"error": "No file name provided"}), 400

    file_path = os.path.join(current_app.BASE_DIR, file_name)

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


@fs_bp.route('/get-sys-info', methods=['GET'])
def get_cwd():
    return jsonify({
        'root_dirs': get_root_directories(),
        'system': platform.system()
    })
from flask import Blueprint, jsonify, request, current_app 
import requests 
import os 

import platform 

from objects import FileMetadataDatabase
from utils import get_root_directories


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
    

@fs_bp.route('/get-ignored-paths', methods=['GET']) 
def get_ignored_dirs(): 
    """Returns a list of all the ignored paths according to the current state of the metadata DB."""
    
    # Get the DB cxn from the app
    metadata_db:FileMetadataDatabase = current_app.file_metadata_db
    
    # Use the metadata db to get the ignored dirs and return the list
    return jsonify({
        'ignored_paths': metadata_db.get_all_ignored_paths()
    })
    

@fs_bp.route('/add-ignored-path', methods=['POST']) 
def add_ignored_path(): 
    """
    Takes in a path and adds it to the DB as an ignored path.
    
    Request body: 
        { 
            "path": "/some/path/to/ignore/" 
        }
        
    Returns: 
        200 | success | Path successfully added to the DB to be ignored. 
        400 | bad request | Not given a path OR the path does not exist in the filesystem (check error in response JSON for context).
        409 | conflict | The given path is already ignored, either by inheritance or explicitly. 
    """
    
    # Get the path from the request body
    request_json:dict = request.get_json()
    new_path:str = request_json.get('path', None)
    
    # Verify a valid path was given
    # Check if given a path at all
    if not new_path: 
        return jsonify({
            'error': 'Not given a path to ignore'
        }), 400
        
    # Check that the given path exists
    elif not os.path.exists(new_path): 
        return jsonify({
            'error': f'Given path "{new_path}" does not exist.'
        }), 400
        
    # Get the FileMetadataDatabase from the current app
    file_metadata_db:FileMetadataDatabase = current_app.file_metadata_db
    
    # Check that the path isn't already ignored 
    if file_metadata_db.check_path_ignored(new_path): 
        return jsonify({
            'error': 'Path is already ignored (either by inheritance or explicitly).'
        }), 409
    
    # Check if the new path is a file or directory
    if os.path.isdir(new_path): type:str = 'directory'
    else: type:str = 'file'
    
    # Add the new path to the DB 
    file_metadata_db.new_ignored_path(new_path, type)
    
    # Return success
    return jsonify({
        'message': f'Path "{new_path}" is now being ignored by indexing.'
    }), 200
    
    
@fs_bp.route('/del-ignored-path', methods=['POST']) 
def del_ignored_path(): 
    """
    Deletes the given path from the "ignored_paths" table in the DB so it will be indexed in the future.
    
    Request body: 
        { 
            "path": "/some/path/"
        }
        
    Returns: 
        200 | success | Path was successfully removed from the ignored paths table and will be indexed in the future.
        400 | bad request | Not given a path OR the given path does not exist in the filesystem. 
    """
    
    # Get the path from the request body
    request_json:dict = request.get_json()
    path:str = request_json.get('path', None)
    
    # Verify a valid path was given
    # Check if given a path at all
    if not path: 
        return jsonify({
            'error': 'Not given a path to delete.'
        }), 400
        
    # Check that the given path exists
    elif not os.path.exists(path): 
        return jsonify({
            'error': f'Given path "{path}" does not exist in the filesystem.'
        }), 400
        
    # Get the FileMetadataDatabase from the current app
    file_metadata_db:FileMetadataDatabase = current_app.file_metadata_db
    
    # Delete the entry from the DB ignored_paths table
    file_metadata_db.del_ignored_path(path)
    
    # Return 
    return jsonify({
        'message': f'Path "{path}" is no longer ignored.'
    })
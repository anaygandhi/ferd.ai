from flask import Blueprint, jsonify, request, current_app 
import requests 
import os 

from utils import extract_json, read_file, tokenize_no_stopwords
from objects import OllamaQueryHandler, FilesystemIndexer, FileMetadataDatabase


# --- Config --- #
# Init blueprint
ai_bp:Blueprint = Blueprint('ai_bp', __name__)


# --- Endpoints --- # 

@ai_bp.route("/ai-assistant", methods=["POST"])
def ai_assistant():
    """Endpoint for AI assistant to interact with the server.
    

    REQ BODY 
        The request body should look like: 

        {
            "action": "<action>",
            "params": {...}
        }

        Accepted actions are: 
            - "generate" : generate an output from the ollama model (note: params must include "prompt")
            - "list_files" : list the files of the given directory (note: params should include "directory", defaults to "/" if not given)
            - "read_file" : reads the given file and returns the first 200 words (note: params must include "file_name")

    RETURNS: 
        200 | success | JSON | the requested content as a JSON object.
        400 | bad request | -- | if the user fails to supply a required parameter or the request body is malformed.
        404 | not found | -- | if the given directory or file is not found.
        500 | internal server error | -- | if some other error occurs when processing the request.
    """
    
    # Extract the required information
    data:dict = request.get_json()
    action:str = data.get("action")
    params:dict = data.get("params", {})

    # Verify that an action was given
    if not action:
        return jsonify({"error": "No action specified"}), 400

    # Act according to the action
    match action: 

        # Action: generate
        case "generate": 
            
            # Get the prompt
            prompt = params.get("prompt", "")

            # Verify that a prompt was given
            if not prompt:
                return jsonify({"error": "No prompt provided for generate action"}), 400

            # Get the ollama query handler from the app
            ollama_query_handler:OllamaQueryHandler = current_app.ollama_query_handler
            
            # Make ollama api req
            try: 
                ollama_response:str = ollama_query_handler.generate(prompt)
            except Exception as e: 
                return jsonify({
                    'error': 'An error occured making the Ollama request.',
                    'message': str(e)
                }), 500
            
            # Return the response
            return jsonify({
                'ollama_response': ollama_response
            })

        # Action list_files
        case "list_files":
            try:
                # Return the list of files in the given directory (or default to root)
                return jsonify({
                    "files": os.listdir(params.get("directory", "/"))
                })

            # Handle exceptions 
            # Given dir does not exist
            except FileExistsError as e: 
                return jsonify({"error": str(e)}), 404  # HTTP 404 -> Not Found
            
            # Some other error
            except Exception as e:
                return jsonify({"error": str(e)}), 500  # HTTP 500 -> Internal Server Error

        # Action read_file
        case "read_file":

            # Get the given filename from the request
            file_name:str = params.get("file_name", "")

            # Verify that a filename is given
            if not file_name:
                return jsonify({"error": "No file name provided"}), 400

            # Construct the path to the file 
            file_path:str = os.path.join(current_app.BASE_DIR, file_name)
            
            # Verify that the path exists
            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            try:

                # Read the file
                with open(file_path, "r", encoding="utf-8") as file:
                    content:str = file.read()

                # Split the file content into words
                words:list[str] = content.split()

                # Return the required information
                return jsonify({    
                    "file_name": file_name,             # Name of the file 
                    "content": ' '.join(words[:200])    # First 200 words of the file content
                })
            
            # Handle exceptions 
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Default case for unknown actions
        case _:
            return jsonify({"error": f"Unknown action: {action}"}), 400
    
    
@ai_bp.route("/search-files", methods=["POST"])
def search_files():
    """Endpoint to find a file in the filesystem based on some query.
    
    REQ BODY: 
        The request body should look like: 
        
        { 
            "query": "<some query>",
            "start_dir": "/top/level/dir/to/search/from/"
        }
        
    RETURNS: 
        200 | success | JSON | a JSON obj with three keys: 'faiss_top_files', 'ollama_response', and 'top_match'.
        400 | bad request | -- | if the user fails to supply a required parameter or the request body is malformed.
        500 | internal server error | -- | if some other error occurs when processing the request.

    """

    # Extract the json from the request body
    try:
        
        # Get JSON
        request_json:dict = request.get_json()

        # Extract user_query and document_content  
        user_query:str = request_json.get("query", "")

        # Verify the information is given
        if not user_query: raise Exception
    
    # Handle errors
    except Exception as e: 
        return jsonify({
            "error": f"Missing 'query'). Given: {request_json}"
        }), 400

    # Check if given a TL dir to start search from
    top_level_dir:str = request_json.get('start_dir', '')

    # Get the indexer and the metadata db from the current app
    filesystem_indexer:FilesystemIndexer = current_app.filesystem_indexer
    metadata_db:FileMetadataDatabase = current_app.file_metadata_db
    
    # Search the index for the query
    # If we're given a TL dir, then we want to filter to just those files in the index 
    if top_level_dir: 
        
        # Get the IDs for all files that are downstream from the TL dir
        file_ids_to_include:list[int] = metadata_db.get_file_ids_by_path_prefix(top_level_dir)
        
        # Use the indexer's subset search to search just these file IDs
        top_file_ids:list[int] = filesystem_indexer.search_subset(
            user_query,
            file_ids_to_include,
            top_k=current_app.K
        )
        
    # If not given a TL dir, then we want to search the entire index
    else: 
        # Use indexer to get the top K documents that match the query
        top_file_ids:list[str] = filesystem_indexer.search_files(
            user_query,
            metadata_db.cursor,
            current_app.K
        )
    
    # If no matches are found, then there is no point in submitting to ollama
    if not top_file_ids: 
        return jsonify({
            'faiss_top_files': [],
            'ollama_response': [],
            'top_match': {
                'file_path': '',
                'confidence': '',
                'context': ''
            }
        })
        
    # Convert the file IDs to abs paths while preserving order
    top_filepaths:list[str] = metadata_db.file_paths_from_ids(top_file_ids)
    
    # Read each of the files into a dict of { filename : file_content }
    documents_dict:dict[str,str] = {
        filepath : read_file(filepath) for filepath in top_filepaths
    }

    # Submit api req to ollama model
    try:
        
        # Get the OllamaQueryHandler from the current app
        ollama_query_handler:OllamaQueryHandler = current_app.ollama_query_handler

        # Call the generate() method 
        ollama_raw_response:str = ollama_query_handler.get_confidence(
            user_query,
            documents_dict
        )

        # Extract the json from the response's response 
        ollama_result_json:dict = extract_json(ollama_raw_response)

        # Get the top match according to ollama
        top_match:str = max(ollama_result_json, key=lambda k: int(ollama_result_json[k]["confidence"]))

        # Return the response json 
        return jsonify({
            'faiss_top_files': top_filepaths,
            'ollama_response': ollama_result_json,
            'top_match': {
                'file_path': top_match,
                'confidence': ollama_result_json[top_match]['confidence'],
                'context': ollama_result_json[top_match]['context']
            }
        })
    
    # Handle errors
    except requests.RequestException as e:
        return jsonify({"error": f"Request to OLLAMA failed: {str(e)}"}), 500
    

@ai_bp.route('/summarize-document', methods=['POST']) 
def summarize_document(): 
    """Passes the given document to the ollama model to summarize."""

    # Get the given request body
    request_json:dict = request.get_json()

    # Extract the absolute filepath from the request body
    abs_filepath:str = request_json.get('filepath', '') 

    # Check that document content was given 
    if not abs_filepath: 
        return jsonify({
            'error': 'Not provided a filepath.'
        }), 400
        
    # Check that the file exists 
    if not os.path.exists(abs_filepath): 
        return jsonify({
            'error': f'The given filepath "{abs_filepath}" does not exist.'
        }), 404
        
    # Get the other details from the request as provided
    max_length:int = request_json.get('max_length', 500)
    overlap:int = request_json.get('overlap', 100)
    
    # Get the OllamaQueryHandler from the current app
    ollama_query_handler:OllamaQueryHandler = current_app.ollama_query_handler
    
    # Summarize the given text
    try: 
        summary:str = ollama_query_handler.recursive_summarize_text(
            read_file(abs_filepath),
            max_summary_len=max_length,
            overlap=overlap
        )
        
    # Value error means the given file type is not readable
    except ValueError: 
        return jsonify({
            'error': f'Given file "{abs_filepath}" is not a supported file type. Accepted types are: PDF, TXT, DOCX.'
        }), 400
        
    # Return the summary
    return jsonify({
        'status': 200,
        'summary': summary,
        'file_path': abs_filepath
    })
    
    


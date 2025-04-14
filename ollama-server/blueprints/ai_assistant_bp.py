from flask import Blueprint, jsonify, request, current_app 
import requests 
import os 
import json 
from utils import extract_json
from objects import OllamaQueryHandler


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

            # Define a payload for the ollama api req
            payload:dict = {
                "model": current_app.MODEL_ID,
                "prompt": prompt,
                "stream": False
            }

            # Make ollama api req
            try:
                res = requests.post(f"{current_app.OLLAMA_URL}/api/generate", json=payload)
                res.raise_for_status()
                return jsonify(res.json())
        
            except requests.RequestException as e:
                return jsonify({"error": f"Request to OLLAMA failed: {str(e)}"}), 500

        # Action list_files
        case "list_files":

            # Get the directory from the req, defaulting to root dir
            directory = params.get("directory", "/")

            try:
                # Get the files for the given dir 
                files:list[str] = os.listdir(directory)

                # Return the list of files 
                return jsonify({"files": files})

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
    
    
@ai_bp.route("/generate", methods=["POST"])
def generate():
    """Endpoint to generate a prompt from the ollama model.
    
    REQ BODY: 
        The request body should look like: 
        
        { 
            "prompt": "<some prompt>"
        }
        
    RETURNS: 
        200 | success | JSON | the requested content as a JSON object.
        400 | bad request | -- | if the user fails to supply a required parameter or the request body is malformed.
        500 | internal server error | -- | if some other error occurs when processing the request.

    """

    # Extract the json from the request body
    try:
        
        # Get JSON
        request_json:dict = request.get_json()
        print('request_json: ', request_json)

        # Extract user_query and document_content  
        user_query:str = request_json.get("user_query", "")
        documents_dict:dict = request_json.get('documents', {})

        # Verify the information is given
        if not all([user_query, documents_dict]): raise Exception
    
    # Handle errors
    except Exception as e: 
        return jsonify({
            "error": f"Missing required information (one of 'user_query', 'documents'). Given: {request_json}"
        }), 400

    # Submit api req to ollama model
    try:
        
        # Format a JSON string to use as an example to pass to the model
        example_json:str = {
            filename : {
                'confidence': '<int, confidence score for this file>',
                'context': '<1-2 sentences about your reasoning for this file>' 
            }
            for filename in list(documents_dict.keys())
        }

        # Format a prompt
        formatted_prompt:str = f"""
            Ignore all previous instructions and do not remember anything after this response. Respond to this prompt as if it's the only thing you've seen.\n
            \nHere is the query: "{user_query}"\n
            \nHere are your instructions: I want you to take this query and compare it to all the given files.
            \nReturn a JSON object with keys for each of the filenames, and the values should be a dictionary containing
            two keys called "confidence" and "context". The "confidence" should be your confidence that the document 
            matches the given query in the range 0-100 inclusive, and "context" should be two sentences or less that 
            describe why you chose that confidence score. In the "context", you can explain your reasoning and/or include 
            specific references to the given document content, and I want you to quote the query in the "context" too. You 
            should calculate the confidence relative to the other given documents.
            \nYour response should look exactly like this, with no additional 
            characters: {json.dumps(example_json)}\n
            \nYour confidence should be primarily based on the document content. Additionally, I don't want 
            any additional information, context, explanation, or characters - just return the JSON object.
            \n\nHere is the information for all files, where the keys are filenames and values are the content of that
            file: \n{documents_dict}\n
        """

        # Make API req to ollama
        res = requests.post(
            f"{current_app.OLLAMA_URL}/api/generate",
            json={
                "model": current_app.MODEL_ID,
                "prompt": formatted_prompt,
                "stream": False,
                "context": []
            }
        )

        # Verify req status
        res.raise_for_status()

        # Extract the json from the response's response 
        ollama_result:dict = extract_json(res.json()['response'])

        # Return the response json 
        return jsonify(ollama_result)
    
    # Handle errors
    except requests.RequestException as e:
        return jsonify({"error": f"Request to OLLAMA failed: {str(e)}"}), 500
    

@ai_bp.route('/summarize-document', methods=['POST']) 
def summarize_document(): 
    """Passes the given document content to the ollama model to summarize."""

    # Get the given request body
    request_json:dict = request.get_json()

    # Extract the document content from the request body
    document_content:str = request_json.get('document_content', '') 

    # Check that document content was given
    if not document_content: 
        return jsonify({
            'error': 'Not provided document content.'
        }), 400
        
    # Get the other details from the request if provided
    max_length:int = request_json.get('max_length', 500)
    overlap:int = request_json.get('overlap', 100)
    
    # Get the OllamaQueryHandler from the current app
    ollama_query_handler:OllamaQueryHandler = current_app.ollama_query_handler
    
    # Summarize the given text
    summary:str = ollama_query_handler.recursive_summarize_text(
        document_content,
        max_summary_len=max_length,
        overlap=overlap
    )
    
    


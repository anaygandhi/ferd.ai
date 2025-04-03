import os
import requests
from metadata_extraction import extract_metadata
from text_extraction import search_in_file
from file_indexer import search_files
import json

OLLAMA_SERVER_URL = 'http://localhost:8321'
FILE_DIRECTORY = './test_pdfs'

def generate_response(file_name, file_content):
    """ Sends file content to Ollama's /generate endpoint with the structured query """
    query = (
        "Is this document a datasheet?"
        "Return a JSON response with two keys: "
        "'file_name' (string) and 'confidence_score' (integer, 1-100 representing your confidence in the fact that this document is a datasheet). "
        " Don't create a new file_name - just the keep the name that is inputted (the path)"
        "Don't use the backticks in the JSON response. "
        "Example: {\"file_name\": \"example.pdf\", \"confidence_score\": 85}"
    )

    data = {
        "prompt": f"{query}\n\nDocument content:\n{file_content}",
    }
    
    try:
        print(f"Sending request for: {file_name}")
        response = requests.post(f"{OLLAMA_SERVER_URL}/generate", json=data, timeout=120)
        response.raise_for_status()  

        response_data = response.json()
        print(f"Ollama response for {file_name}: {response_data['response']}")

        return response_data['response']
    
    except requests.Timeout:
        print(f"Error: Request timed out for '{file_name}'. Trying again with a longer timeout...")
        return None  
    except requests.RequestException as e:
        print(f"Error: Request failed for '{file_name}': {e}")
        return None


def send_files_to_ollama(files):
    best_match = None
    highest_score = -float('inf')  

    for file in files:
        file_path = os.path.join(FILE_DIRECTORY, file)
        
        try:
            # Extract text from PDF, DOCX, or TXT files
            file_content = search_in_file(file_path)

            # Extract metadata from the file
            metadata = extract_metadata(file_path)
            print(f"Metadata for {file}: {metadata}")

            # Send only the first 200 words of the content
            words = file_content.split()[:200]
            first_200_words = ' '.join(words)

            # Generate response by sending first 200 words
            response_data = generate_response(file, first_200_words)

            if response_data:
                response_obj = json.loads(response_data)
                score = response_obj.get("confidence_score", None)
                
                if score is None:
                    print(f"Warning: No confidence score received for '{file}'. Skipping.")
                    continue
                
                print(f"Confidence score for '{file}': {score}")
                
                if score > highest_score:
                    highest_score = score
                    best_match = file
                    
            else:
                print(f"Failed to get a valid response for {file}. Skipping.")
                
        except Exception as e:
            print(f"Error during processing file '{file}': {e}")

    if best_match:
        print(f"The best matching file for the query is: '{best_match}' with a confidence score of {highest_score}")
    else:
        print("No suitable match found.")


if __name__ == "__main__":
    search_query = "Find the datasheet"
    top_files = search_files(search_query)
    send_files_to_ollama(top_files)

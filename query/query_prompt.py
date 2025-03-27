import requests
import json

OLLAMA_SERVER = "http://127.0.0.1:8321"

def get_file_list():
    """Fetches the list of files from the root directory using the Flask API."""
    response = requests.get(f"{OLLAMA_SERVER}/list-files")
    if response.status_code == 200:
        file_list = response.json().get("files", [])
        return ", ".join(file_list) 
    else:
        return "Error fetching files."

def query_model():
    """Prompts user for input and sends the request to the Flask API."""
    file_list = get_file_list()
    prompt = input("Enter a prompt: ")

    full_prompt = f"{prompt}\n\nFiles in root directory: {file_list}"

    payload = {"prompt": full_prompt}
    headers = {"Content-Type": "application/json"}

    response = requests.post(f"{OLLAMA_SERVER}/generate", data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        print("Response:", response_json.get("response", "No response found"))
    else:
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    query_model()

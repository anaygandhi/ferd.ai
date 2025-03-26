import requests
import json
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:8321/generate")
MODEL_ID = os.getenv("INFERENCE_MODEL", "llama3.2:1b-instruct-fp16")

def get_response_from_model(prompt):
    payload = {"prompt": prompt}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(OLLAMA_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("response", "No response found")
        else:
            return f"Error: {response.status_code}, {response.text}"
    except requests.RequestException as e:
        return f"Error: {str(e)}"

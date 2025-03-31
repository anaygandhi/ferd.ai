import os
import json
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:8321/generate")

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

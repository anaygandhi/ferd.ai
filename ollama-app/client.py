import requests
import json

def query_model(prompt):
    """
    Query the Ollama server running on localhost:8321
    """
    url = "http://localhost:8321/generate"
    
    payload = {
        "prompt": prompt,
        "max_tokens": 10
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Test basic connectivity to Ollama API
response = requests.get("http://localhost:11434/api/version")
print(f"Ollama API Response: {response.status_code}")
print(response.json() if response.status_code == 200 else "Failed to connect")

# Example usage
if __name__ == "__main__":
    prompt = "What is artificial intelligence?"
    result = query_model(prompt)
    print(json.dumps(result["response"], indent=2))
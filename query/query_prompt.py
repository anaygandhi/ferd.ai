import requests
import json


url = "http://127.0.0.1:8321/generate"
prompt = input("Enter a prompt: ")

# Send prompt
payload = {"prompt": prompt}
headers = {"Content-Type": "application/json"}



response = requests.post(url, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    response_json = response.json()
    print("Response:", response_json.get("response", "No response found"))
else:
    print(f"Error: {response.status_code}, {response.text}")

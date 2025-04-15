
import os 
from text_extraction import read_file
import requests 


INPUT_DIR:str = '../test_pdfs'
OUTPUT_DIR:str = 'test-results/test_summaries'
OLLAMA_SERVER_URL = 'http://localhost:8321'


# Create the output dir if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Iterate over all the files in the input dir
for filename in os.listdir(INPUT_DIR):

    # Construct full filepath
    filepath:str = os.path.join(INPUT_DIR, filename)

    # Read the file 
    file_content:str = read_file(filepath)

    # Submit the content to ollama 
    response:requests.Response = requests.post(
        OLLAMA_SERVER_URL + '/summarize-document', 
        json={'document_content': file_content}
    )

    # Extract model's response from the response json 
    response_json:dict = response.json()['response']

    # Handle response 
    print(f'\n\033[94mGot response for file "{filename}": \033[0m', response_json)




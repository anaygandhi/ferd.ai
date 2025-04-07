import requests 
import json 
import os 


def get_ollama_response(all_file_info:dict, given_query:str, url:str) -> dict|None:
    """Sends file content to the given URL with the structured query; the URL should be to the flask server's 
    /generate endpoint."""

    data:dict = {
        "user_query": given_query,
        "documents": all_file_info
    }

    # Make API req to flask server
    try:
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()  

        response_data = response.json()
        return response_data
    
    except requests.Timeout:
        print(f"\033[91mERROR in generate_response(): \033[0mRequest timed out for '{all_file_info}'. Trying again with a longer timeout...")
        return None  
    except requests.RequestException as e:
        print(f"\033[91mERROR in generate_respones(): \033[0mRequest failed for '{all_file_info}': {e}")
        return None
    


def send_files_to_ollama(all_file_info:dict[str, dict], search_query:str, url:str, x_words:int=500) -> dict:

    # Send only the first [x_words] of the content for each file
    trimmed_file_info:dict[str, dict] = {
         filename: ' '.join(file_content.split()[:x_words])  
         for filename, file_content in all_file_info.items()
    }

    # Generate response by sending first X words
    response_data:dict = get_ollama_response(trimmed_file_info, search_query, url)

    print('response_data: ', response_data)
    
    # Handle the response
    if response_data:

        # Parse the confidence scores into integers
        for k,v in response_data.items(): 
            tmp_v:dict = v
            tmp_v['confidence'] = int(tmp_v['confidence'])
            response_data[k] = tmp_v
        
        # Return the result 
        return response_data
    else:
        print(f"\033[91mERROR in send_files_to_ollama(): \033[0mFailed to get a valid response from the API.")
        return {}

import tiktoken
from transformers import AutoTokenizer 


class OllamaQueryHandler: 

    # STATIC ATTRIBUTES
    # Relevant URL endpoints
    GENERATE_ENDPT:str = '/generate'

    # Llama compatible tokenizer (from huggingface)
    TOKENIZER:AutoTokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

    # DYNAMIC ATTRIBUTES
    ollama_url:str      # URL to the Ollama model/server (e.g. http://localhost:1143)
    model:str           # The model being used by the server (e.g. llama3.2:3b-instruct-fp16)

    # Attrs set with combos of static and dynamic attrs
    generate_url:str            # [ollama_url] + [GENERATE_ENDPT]


    def __init__(self, ollama_url:str):

        # Set dyn attrs
        self.ollama_url = ollama_url if not ollama_url.endswith('/') else ollama_url[:-1]
        
        # Create attrs from combos of static/dyn attrs
        self.generate_url = ollama_url + OllamaQueryHandler.GENERATE_ENDPT


    def summarize_document(self, document_text:str) -> str: 
        """
        Takes in a document as text and queries the ollama model to summarize the document.
        
        Parameters: 
            document_text (str): The full document text as a string.

        Returns
            str: The summarized document.
        """
        raise NotImplementedError
    

    @classmethod
    def chunk_text(cls, text:str, chunk_size:int=2000) -> list[str]: 
        """
        Breaks input text into chunks of `chunk_size` tokens using a tokenizer.
        
        Parameters:
            text (str): The input text to be chunked.
            chunk_size (int): The maximum number of tokens per chunk.
            model_name (str): Tokenizer model name (e.g., 'gpt2').

        Returns:
            list[str]: A list of text chunks.
        """
        input_ids:list = OllamaQueryHandler.TOKENIZER.encode(text, add_special_tokens=False)
        chunks:list[str] = []

        # Iterate over the text in [chunk_size] chunks
        for i in range(0, len(input_ids), chunk_size):
            chunk_ids = input_ids[i:i+chunk_size]
            chunk = OllamaQueryHandler.TOKENIZER.decode(chunk_ids, skip_special_tokens=True)
            chunks.append(chunk)

        # Return the populated array of chunks
        return chunks
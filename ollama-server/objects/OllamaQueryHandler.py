import tiktoken
from ollama import Client as OllamaClient
from ollama import GenerateResponse


class OllamaQueryHandler: 

    ollama_client:OllamaClient  # Client class instance (from ollama)
    model:str                   # The model being used by the server (e.g. llama3.2:3b-instruct-fp16)
    
    # NOTE: static encoding for tokenizer 
    encoding:tiktoken.Encoding = tiktoken.get_encoding("cl100k_base")
    

    def __init__(self, ollama_client:OllamaClient, model:str):
        self.ollama_client = ollama_client
        self.model = model 
        

    def summarize_text(self, text:str, max_length:int=500) -> str: 
        """
        Takes in a document as text and queries the ollama model to summarize the document.
        
        Parameters: 
            document_text (str): The full document text as a string.

        Returns
            str: The summarized document.
        """
            
        # Format a prompt 
        formatted_prompt:str = f"""
            Summarize the following text into less than or equal to {max_length} words, returning only the summary and no extra 
            context, characters, or words. Additionally, the summary should read like a coherent passage and summarize the main points
            of the text, avoid things like "the text says", and avoid redundant information: 
            \n{text}
        """

        # Make req to ollama client
        response:GenerateResponse = self.ollama_client.generate(
            model=self.model,
            prompt=formatted_prompt
        )
        
        # Return the response json 
        return response.response


    def chunk_text(self, text:str, chunk_size:int=1975, overlap:int=100) -> list[str]: 
        """
        Breaks input text into chunks of `chunk_size` tokens using a tokenizer.
        
        Parameters:
            text (str): The input text to be chunked.
            chunk_size (int): The maximum number of tokens per chunk.
            model_name (str): Tokenizer model name (e.g., 'gpt2').

        Returns:
            list[str]: A list of text chunks.
        """
        # Init vars
        tokens:list[str] = OllamaQueryHandler.tokenize(text)
        chunks:list[list[str]] = []
        i:int = 0
        
        # Create chunks of chunk_size
        while i < len(tokens):
            chunk_tokens = tokens[i:i+chunk_size]
            chunks.append(OllamaQueryHandler.detokenize(chunk_tokens))
            
            # Incl overlap for context retention
            i += chunk_size - overlap  
            
        # Return the populated array of chunks
        return chunks
    
    
    def recursive_summarize_text(self, text:str, chunk_size:int=1975, max_summary_len:int=500, overlap:int=100) -> str: 
        """Takes in a long text (> chunk_size) and recursively summarizes until the result is <= max_summary_length. 
        
        Parameters: 
            text (str): the text to summarize.
            chunk_size (int, optional): size of the chunks to tokenize the original text into. Defaults to 2000.
            max_summary_len (int, optional): maximum size of the returned summary. Defaults to 500. 
            overlap (int, optional): the window of overlap for tokens in each chunk to preserve context. Defaults to 100.
            
        Returns: 
            str: a summary of the input text.
        """
        
        # Start with summary_text equal to the input text incase the input text is already less than the max summary length
        summary_text:str = text
    
        # Recursively summarize until under token limit        
        while len(OllamaQueryHandler.tokenize(summary_text)) > max_summary_len:
                        
            # Split this summary into chunks
            chunks:list[list[str]] = self.chunk_text(
                summary_text, 
                chunk_size=chunk_size, 
                overlap=overlap
            )
            
            # Summarize each chunk
            summaries:list[str] = [self.summarize_text(chunk) for chunk in chunks]
            
            # Concatenate the summaries with newlines
            summary_text:str = "\n\n".join(summaries)

        # Return the final summary
        return summary_text
        
        
    @classmethod
    def tokenize(cls, text:str) -> list[int]: 
        """Wrapper for OllamaQueryHandler.encoding.encode()."""
        return OllamaQueryHandler.encoding.encode(text)
    

    @classmethod
    def detokenize(self, tokens:list[str|int]) -> str: 
        """Wrapper for OllamaQueryHandler.tokenizer.decode()."""
        return OllamaQueryHandler.encoding.decode(tokens)
        
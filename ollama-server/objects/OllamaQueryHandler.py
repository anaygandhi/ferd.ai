import tiktoken
import json 

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
        """
        Takes in a long text (> chunk_size) and recursively summarizes until the result is <= max_summary_length. 
        
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
        
    
    def generate(self, prompt:str) -> str: 
        """
        Submits the given prompt to the ollama client's generate() function.

        Parameters: 
            prompt (str): the prompt to submit.

        Returns: 
            str: the Ollama model's response as a string. 
        """
        return self.ollama_client.generate(prompt)['response']


    def get_confidence(self, query:str, documents_dict:dict[str,str], first_n_toks:int=600) -> dict: 
        """
        Prompts the Ollama model to generate a confidence score that the given document text matches the given query. 

        Parameters: 
            query (str): the user's query to compare to.
            documents_dict (dict[str, str]): keys are the document names (filenames) and the values are the document content (as str).
            first_n_toks (int, optional): specify how many tokens to take for each document. Defaults to 600. 
        Returns: 
            dict: a dict with two keys: "context", which is Ollama's arbitrary context as to why the document matches the
            query, and "confidence", which is an integer (0-100 inclusive) that represents Ollama's confidence that the
            given document matches the given query.
        """

        # Format a JSON string to use as an example to pass to the model
        example_json:str = {
            filename : {
                'confidence': '<int, confidence score for this file>',
                'context': '<1-2 sentences about your reasoning for this file>' 
            }
            for filename in list(documents_dict.keys())
        }

        # Convert the documents dict to contain just the first [first_n_toks] tokens of each document content 
        trimmed_document_contents:dict[str, str] = {
            doc_name : self.detokenize(
                self.tokenize(doc_content)[:first_n_toks]
            )
            for doc_name, doc_content in documents_dict.items()
        }

        # Format a prompt to submit
        formatted_prompt:str = f"""
            Ignore all previous instructions and do not remember anything after this response. Respond to this prompt as if it's the only thing you've seen.\n
            \nHere is the query: "{query}"\n
            \nHere are your instructions: I want you to take this query and compare it to all the given files.
            \nReturn a JSON object with keys for each of the filenames, and the values should be a dictionary containing
            two keys called "confidence" and "context". The "confidence" should be your confidence that the document 
            matches the given query in the range 0-100 inclusive, and "context" should be two sentences or less that 
            describe why you chose that confidence score. In the "context", you can explain your reasoning and/or include 
            specific references to the given document content, and I want you to quote the query in the "context" too. You 
            should calculate the confidence relative to the other given documents.
            \nYour response should look exactly like this, with no additional 
            characters: {json.dumps(example_json)}\n
            \nYour confidence should be primarily based on the document content. Additionally, I don't want 
            any additional information, context, explanation, or characters - just return the JSON object.
            \n\nHere is the information for all files, where the keys are filenames and values are the content of that
            file after stopwords were removed: \n{trimmed_document_contents}\n
        """

        print(f'\nSubmitting prompt with {len(self.tokenize(formatted_prompt))} tokens...\n')

        # Submit the query to ollama 
        response:str = self.generate(formatted_prompt)

        print('\033[92mOLLAMA RESPONSE: \n\033[0m', response)

        return response 
    

    @classmethod
    def tokenize(cls, text:str) -> list[int]: 
        """Wrapper for OllamaQueryHandler.encoding.encode()."""
        return OllamaQueryHandler.encoding.encode(text)
    

    @classmethod
    def detokenize(self, tokens:list[str|int]) -> str: 
        """Wrapper for OllamaQueryHandler.tokenizer.decode()."""
        return OllamaQueryHandler.encoding.decode(tokens)
        
import os
import requests
import json
from typing import List, Dict, Any
from file_processing import process_directory
from vector_store import VectorStore

class RAGSystem:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.vector_store = VectorStore()
        self.ollama_url = ollama_url
        
    def index_directory(self, directory_path: str):
        """Process and index files from a directory."""
        print(f"Indexing files in {directory_path}...")
        documents = process_directory(directory_path)
        print(f"Found {len(documents)} documents")
        
        self.vector_store.add_documents(documents)
        print("Indexing complete")
        
    def query(self, query_text: str, max_tokens: int = 512) -> Dict[str, Any]:
        """Perform RAG query: retrieve documents and generate response."""
        # Step 1: Retrieve relevant documents
        results = self.vector_store.search(query_text, k=3)
        
        # Step 2: Format context from retrieved documents
        context = "\n\n".join([
            f"Document: {r['file_name']}\n{r['text']}" 
            for r in results
        ])
        
        # Step 3: Create prompt with context
        prompt = f"""You are a helpful assistant for searching through files. 
Use ONLY the following context to answer the question. 
If you cannot find the answer in the context, say that you don't know.

CONTEXT:
{context}

QUESTION: {query_text}

ANSWER:"""
        
        # Step 4: Generate response using Ollama
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": "llama3.2:1b-instruct-fp16",
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            return {"error": f"Error: {response.text}"}
        
        # Step 5: Return results
        return {
            "query": query_text,
            "response": response.json()["response"],
            "sources": [
                {
                    "file_name": r["file_name"],
                    "file_path": r["file_path"],
                    "score": r["score"]
                } for r in results
            ]
        }
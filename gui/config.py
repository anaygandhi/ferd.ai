import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:8321/generate")
MODEL_ID = os.getenv("INFERENCE_MODEL", "llama3.2:1b-instruct-fp16")

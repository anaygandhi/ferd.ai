import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import fitz
import sqlite3
import numpy as np
from docx import Document
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm  
from file_indexing.metadata_extraction import extract_metadata
from file_indexing.text_extraction import search_in_file

model = SentenceTransformer('all-MiniLM-L6-v2')  
embedding_dim = 384

# FAISS index setup
if os.path.exists('faiss_index.bin'):
    index = faiss.read_index('faiss_index.bin')
    print("Loaded existing FAISS index.")
else:
    index = faiss.IndexFlatL2(embedding_dim)

# SQLite setup
conn = sqlite3.connect('file_metadata.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS file_metadata (
    id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE,
    file_name TEXT,
    file_size INTEGER,
    created TEXT,
    modified TEXT,
    embedding BLOB
)
''')
conn.commit()

def index_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in tqdm(files, desc="Indexing files"):
            file_path = os.path.join(root, file)

            if file_path.endswith(('.pdf', '.docx', '.txt')):
                try:
                    cursor.execute('SELECT COUNT(*) FROM file_metadata WHERE file_path = ?', (file_path,))
                    if cursor.fetchone()[0] > 0:
                        print(f"File {file_path} already exists in the database. Skipping insertion.")
                        continue

                    metadata = extract_metadata(file_path)
                    file_text = search_in_file(file_path)
                    embedding = model.encode(file_text)

                    if embedding is None or len(embedding) != embedding_dim:
                        print(f"Failed to generate valid embedding for {file_path}. Skipping.")
                        continue

                    embedding_array = np.array(embedding, dtype=np.float32).reshape(1, -1)
                    index.add(embedding_array)

                    cursor.execute('''
                    INSERT INTO file_metadata (file_path, file_name, file_size, created, modified, embedding)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        file_path,
                        os.path.basename(file_path),
                        metadata.get('file_size', 0),
                        metadata.get('created', ''),
                        metadata.get('modified', ''),
                        embedding_array.tobytes()
                    ))
                    conn.commit()

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    faiss.write_index(index, 'faiss_index.bin')
    print("FAISS index saved.")

def search_files(query, top_k=5):
    query_embedding = model.encode(query)
    query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    if query_embedding.shape[1] != embedding_dim:
        print("Query embedding has incorrect dimensions. Aborting search.")
        return []

    _, indices = index.search(query_embedding, top_k)

    print(f"FAISS indices: {indices}")

    file_names = []
    for idx in indices[0]:
        if idx != -1:
            cursor.execute('SELECT file_name FROM file_metadata WHERE id = ?', (idx+1,))
            result = cursor.fetchone()
            if result:
                file_names.append(result[0])

    return file_names

# Example usage
index_directory('/Users/anaygandhi/Downloads/CS311/')

query = "Find pdf files"
top_files = search_files(query)
print(f"Top files: {top_files}")

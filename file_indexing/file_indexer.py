import os
import sys
import sqlite3
import numpy as np
import faiss
from tqdm import tqdm
from sklearn.preprocessing import normalize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from file_indexing.metadata_extraction import extract_metadata
from file_indexing.text_extraction import search_in_file
from sentence_transformers import SentenceTransformer
import logging
import torch

# Suppressing warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
warnings.filterwarnings("ignore", category=UserWarning, message=".*_register_pytree_node*")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup SentenceTransformer model for embedding
model = SentenceTransformer('paraphrase-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')
embedding_dim = 384  # Dimensionality of the embeddings

# FAISS index setup
if os.path.exists('faiss_index.bin'):
    index = faiss.read_index('faiss_index.bin')
    logger.info(f"Loaded existing FAISS index with {index.ntotal} embeddings.")
else:
    index = faiss.IndexFlatL2(embedding_dim)
    logger.info("Initialized a new FAISS index.")

# SQLite setup
conn = sqlite3.connect('file_metadata.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS file_metadata (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    file_name TEXT,
    file_size INTEGER,
    created TEXT,
    modified TEXT,
    embedding BLOB
)
''')
conn.commit()

# Wrapper class for FaissDB
class FaissDB:
    def __init__(self, db_conn, index, model, embedding_dim=384):
        self.conn = db_conn
        self.cursor = self.conn.cursor()
        self.index = index
        self.model = model
        self.embedding_dim = embedding_dim

    def get_embeddings(self, documents):
        embeddings = []
        for doc in documents:
            logger.info(f"Generating embedding for document: {doc[0]}")
            embedding = self.model.encode(doc[1])
            embedding = np.array(embedding, dtype=np.float32).reshape(1, -1)
            embeddings.append(embedding)
        embeddings = np.array(embeddings)
        return embeddings

    def index_documents(self, documents):
        embeddings = self.get_embeddings(documents)
        embeddings = normalize(embeddings, norm='l2')
        self.index.add(embeddings)
        logger.info(f"Indexed {len(documents)} documents.")
    
    def save_index(self, filename):
        faiss.write_index(self.index, filename)
        logger.info(f"Index saved to {filename}.")

    def search(self, query, top_k=3):
        query_embedding = self.model.encode(query)
        query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        query_embedding = normalize(query_embedding, norm='l2')

        if query_embedding.shape[1] != self.embedding_dim:
            logger.error("Query embedding has incorrect dimensions. Aborting search.")
            return []

        if self.index.ntotal == 0:
            logger.error("FAISS index is empty. Please index documents first.")
            return []

        _, indices = self.index.search(query_embedding, top_k)
        return indices[0]

    def get_document(self, faiss_index):
        self.cursor.execute("SELECT file_name, file_path FROM file_metadata WHERE id = ?", (faiss_index,))
        result = self.cursor.fetchone()
        if result:
            return result
        else:
            return None, None


# Directory scanning and indexing
def index_directory(directory_path):
    db = FaissDB(db_conn=conn, index=index, model=model)

    for root, dirs, files in os.walk(directory_path):
        for file in tqdm(files, desc="Indexing files"):
            file_path = os.path.join(root, file)

            if file_path.endswith(('.pdf', '.docx', '.txt')):
                try:
                    cursor.execute('SELECT COUNT(*) FROM file_metadata WHERE file_path = ?', (file_path,))
                    if cursor.fetchone()[0] > 0:
                        logger.info(f"File {file_path} already exists in the database. Skipping.")
                        continue

                    metadata = extract_metadata(file_path)
                    file_text = search_in_file(file_path)
                    embedding = model.encode(file_text)

                    if embedding is None or len(embedding) != embedding_dim:
                        logger.warning(f"Failed to generate valid embedding for {file_path}. Skipping.")
                        continue

                    embedding_array = np.array(embedding, dtype=np.float32).reshape(1, -1)
                    embedding_array = normalize(embedding_array, norm='l2')

                    # Insert metadata and embeddings into the database
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

                    # Adding embedding to FAISS index
                    db.index_documents([(file_path, file_text)])

                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

    db.save_index('faiss_index.bin')
    logger.info(f"FAISS index saved with {index.ntotal} embeddings.")


# Perform similarity search in FAISS
def search_files(query, top_k=3):
    db = FaissDB(db_conn=conn, index=index, model=model)
    indices = db.search(query, top_k)

    if not indices:
        return []

    file_names = []
    for idx in indices:
        if idx != -1:
            file_name, file_path = db.get_document(idx + 1)
            if file_name:
                file_names.append((file_name, file_path))
    return file_names


# Example usage:
index_directory('/Users/anaygandhi/Downloads/CS311/')

query = "Find homework files"
top_files = search_files(query, top_k=5)

logger.info(f"Top files: {top_files}")

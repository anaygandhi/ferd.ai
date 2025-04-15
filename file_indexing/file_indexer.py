import sqlite3 as sql
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm  

# Modify sys path for util imports 
import sys
import os

parent_dir:str = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ollama-server'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
# Util imports 
from utils import index_directory, search_files


# --- Config --- #
# Config vars
INDEX_DIR:str = 'index/'
EMBEDDING_DIM:int = 384

# Construct paths to the faiss_index.bin and file_metadata.db files
INDEX_BIN_PATH:str = os.path.join(INDEX_DIR, 'faiss_index.bin')
METADATA_DB_PATH:str = os.path.join(INDEX_DIR, 'file_metadata.db')


# --- Setup --- #
# Create model
model = SentenceTransformer('all-MiniLM-L6-v2')  

# Create index dir if it doesn't exist
os.makedirs(INDEX_DIR, exist_ok=True)

# FAISS index setup
if os.path.exists(INDEX_BIN_PATH):
    index:faiss.IndexFlatL2 = faiss.read_index(INDEX_BIN_PATH)
    print("\033[92mLoaded existing FAISS index.\033[0m")
else:
    print('Creating index')
    index:faiss.IndexFlatL2 = faiss.IndexFlatL2(EMBEDDING_DIM)

# SQLite setup
cxn:sql.Connection = sql.connect(METADATA_DB_PATH)
cursor:sql.Cursor = cxn.cursor()


# --- SQLite DB setup --- #
# Create the file_metadata table if it doesn't already exist
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

# Commit changes
cxn.commit()


# --- Indexer --- #
# Index the directory
index_directory(
    '../test_pdfs',     # Input dir path
    model,              # Sentence transformer model
    cxn,                # Sqlite connection
    cursor,             # Sqlite cursor
    EMBEDDING_DIM,      # Embedding dim 
    INDEX_BIN_PATH,
    index
)
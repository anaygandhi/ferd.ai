import os
import json
from tqdm import tqdm
import faiss 
import sqlite3 as sql
from sentence_transformers import SentenceTransformer

from utils import send_files_to_ollama, tokenize_no_stopwords, search_files, read_file


# --- Config --- #
OLLAMA_SERVER_URL:str = 'http://localhost:8321'
INPUT_FILE_DIR:str = '../test_pdfs'
INDEX_FILE_DIR:str = 'index/'
EMBEDDING_DIM:int = 384
K:int = 3

# Construct the index bin and metadata db paths
INDEX_BIN_PATH:str = os.path.join(INDEX_FILE_DIR, 'faiss_index.bin')
METADATA_DB_PATH:str = os.path.join(INDEX_FILE_DIR, 'file_metadata.db')

search_query:str = "sharks"


# --- Setup --- #
# Load the index
index:faiss.IndexFlatL2 = faiss.read_index(INDEX_BIN_PATH)

# SQLite connection
cxn:sql.Connection = sql.connect(METADATA_DB_PATH)
cursor:sql.Cursor = cxn.cursor()

# Create model
model:SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')  

# Get the filename and content for all files in the input directory
all_file_info:dict[str, dict] = {
    filename : read_file(os.path.join(INPUT_FILE_DIR, filename))
    for filename in tqdm(os.listdir(INPUT_FILE_DIR), total=len(os.listdir(INPUT_FILE_DIR)), desc="Extracting files' content")
}


# --- Search --- #
# Calculate the top K files 
top_files:list[str] = search_files(
    search_query, 
    model,
    EMBEDDING_DIM,
    index,
    cursor,
    top_k=K
)


# --- Ollama query --- #
# Send the top K files to ollama for analysis
ollama_response:dict = send_files_to_ollama(
    { filename : ' '.join(tokenize_no_stopwords(all_file_info[filename])) for filename in top_files }, 
    search_query,
    OLLAMA_SERVER_URL + '/generate'
)

# Print results
print('\033[92mOllama response: \033[0m\n', ollama_response)
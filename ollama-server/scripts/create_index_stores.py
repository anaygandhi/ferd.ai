from configparser import ConfigParser
import os 
from sentence_transformers import SentenceTransformer
import faiss 
import sqlite3 as sql

# Modify sys path for util imports 
import sys
import os

parent_dir:str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils import index_filesystem


# NOTE: the [INPUT_DIR_PATH] is the TL directory to start indexing from
# note that ALL CHILD DIRECTORIES of the [INPUT_DIR_PATH] will be traversed 
# and indexed
INPUT_DIR_PATH:str = '../test-pdfs'


# ---- Config ---- #
# Load config
config:ConfigParser = ConfigParser() 
config.read('config/config.conf')

# Extract required vars
INDEX_BIN_PATH:str = config['paths']['INDEX_BIN_PATH']
METADATA_DB_PATH:str = config['paths']['METADATA_DB_PATH']
EMBEDDING_DIM:int = int(config['index']['EMBEDDING_DIM'])

# Create the output directories if they don't exist
os.makedirs(os.path.dirname(INDEX_BIN_PATH), exist_ok=True)
os.makedirs(os.path.dirname(METADATA_DB_PATH), exist_ok=True)

# NOTE: Prompt user for confirmation to overwrite existing index and DB 
# if they already exist 

# Overwrite index?
if os.path.exists(INDEX_BIN_PATH): 
    print(f'\033[93mNOTICE: \033[0mthere is already an existing index BIN at "{INDEX_BIN_PATH}" - executing this script will overwrite this file.')
    idx_overwrite_inp:str = input('\033[93mDo you want to continue [Y/N]?\033[0m ').upper()

    # Make sure correct format 
    while not idx_overwrite_inp in ['Y', 'N']: 
        print(f'\033[91mERROR: \033[0mgiven invalid input "{idx_overwrite_inp}" - expecting ["Y" | "N"].')
        idx_overwrite_inp = input('\033[93mDo you want to continue [Y/N]?\033[0m ').upper()

    # Quit if no
    if idx_overwrite_inp == 'N': 
        print('\033[93mNOTICE: \033[0mexiting...')
        quit()
    # Remove if yes
    else: 
        os.remove(INDEX_BIN_PATH)

# Overwrite DB? 
if os.path.exists(METADATA_DB_PATH): 
    print(f'\033[93mNOTICE: \033[0mthere is already an existing database file at "{METADATA_DB_PATH}" - executing this script will overwrite this file.')
    overwrite_db_inp:str = input('\033[93mDo you want to continue [Y/N]?\033[0m ').upper()

    # Make sure correct format 
    while not overwrite_db_inp in ['Y', 'N']: 
        print(f'\033[91mERROR: \033[0mgiven invalid input "{METADATA_DB_PATH}" - expecting ["Y" | "N"].')
        overwrite_db_inp = input('\033[94mDo you want to continue [Y/N]?\033[0m ').upper()

    # Quit if no
    if overwrite_db_inp == 'N': 
        print('\033[93mNOTICE: \033[0mexiting...')
        quit()
    # Remove file if yes
    else: 
        os.remove(METADATA_DB_PATH)

# ---- Setup ---- #
# Create model
model:SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')  

# Create index 
index:faiss.IndexFlatL2 = faiss.IndexFlatL2(EMBEDDING_DIM)

# SQLite setup
cxn:sql.Connection = sql.connect(METADATA_DB_PATH)
cursor:sql.Cursor = cxn.cursor()


# --- SQLite DB setup --- #
print('\033[94mCreating metadata database...\033[0m')

# Create the file_metadata table if it doesn't already exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS file_metadata (
        id INTEGER PRIMARY KEY,
        file_path TEXT UNIQUE,
        file_name TEXT,
        file_size INTEGER,
        file_sha256 TEXT,
        created TEXT,
        modified TEXT,
        embedding BLOB
    )
''')

# Commit changes
cxn.commit()


# --- Indexer --- #
# Index the directory
index_filesystem(
    INPUT_DIR_PATH,     # Input dir path
    model,              # Sentence transformer model
    cxn,                # Sqlite connection
    cursor,             # Sqlite cursor
    EMBEDDING_DIM,      # Embedding dim 
    INDEX_BIN_PATH,
    index,
    verbose=True
)
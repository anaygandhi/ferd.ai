import os 
import faiss 
import sqlite3 as sql
import numpy as np 

from sentence_transformers import SentenceTransformer 
from .FileMetadataDatabase import FileMetadataDatabase
from utils import print_log, extract_metadata, hash_file_sha256, read_file


class FilesystemIndexer: 
    
    start_dir:str                            # The top level (TL) dir that this indexer starts at
    file_metadata_db:FileMetadataDatabase    # DB connection wrapper
    index_bin_path:str                       # Path to the Faiss index binary file 
    embedding_dim:int                        # Embedding dimensions for the index
    sentence_transformer:SentenceTransformer # Sentence transformer model for indexing files
    
    
    def __init__(self, start_dir:str, metadata_db_path:str, index_bin_path:str, embedding_dim:int): 
        self.start_dir = start_dir
        self.file_metadata_db = FileMetadataDatabase(metadata_db_path)
        self.index_bin_path = index_bin_path
        self.embedding_dim = embedding_dim
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')  
        
    
    def index_filesystem(self, overwrite:bool=False, verbose:bool=False) -> None: 
        """Indexes the filesystem starting at [self.start_dir] and recursively traverses child directories. 
        
            Parameters: 
                overwrite (bool, optional): "True" means that if the index & DB exist already then they will be overwritten from scratch; "False" means that only changed files
                    will be updated (i.e. where the stored hash does not match the computed hash). If the index does not exist, then it will be created in either case. Defaults to False. 
                verbose (bool, optional): "True" means print debug info; "False" means silent run and print only fatal errors. Defaults to False. 
                
            Returns: 
                None: updates/creates the faiss index and db at [self.index_bin_path] and [self.metadata_db_path] respectively. 
        """
        
        # ---- Setup ---- #
        # Create the dirs for the index bin if it doesn't exist
        os.makedirs(os.path.dirname(self.index_bin_path), exist_ok=True)
        
        # Check if overwriting existing data 
        if overwrite: 
            
            # Info print 
            if verbose: print_log('WARN', 'index_filesystem()', f'Overwriting existing index at "{self.index_bin_path}".')
            
            # Delete the existing index 
            if os.path.exists(self.index_bin_path): os.remove(self.index_bin_path)
            
            # Create the index 
            index:faiss.IndexFlatL2 = faiss.IndexFlatL2(self.embedding_dim)
        
        # If NOT overwriting, then just make the SQL connection and read the existing index
        else: 
            
            # Info print
            if verbose: print_log('INFO', 'index_filesystem()', f'Reading existing index at "{self.index_bin_path}".')
            
            # Read the existing index or create it if it doesn't exist
            if os.path.exists(self.index_bin_path): index:faiss.IndexFlatL2 = faiss.read_index(self.index_bin_path)
            else: index:faiss.IndexFlatL2 = faiss.IndexFlatL2(self.embedding_dim)
            
        # ---- Indexing ---- #
        # Iterate over all the child dirs in [self.start_dir] and recursively index each file
        if verbose: 
            print_log('INFO', 'Filesystem.index_filesystem()', f'Starting indexing from "{self.start_dir}". Files: {os.listdir(self.start_dir)}')
        
        for root, dirs, files in os.walk(self.start_dir):
            
            # Info print 
            if verbose: print_log('INFO', 'FilesystemIndexer.index_filesystem()', f'Reading {len(files)} from {root}.')
            
            # Iterate over all the files in this dir
            for file in files:
                
                # Construct the full filepath
                full_path = os.path.join(root, file)

                # Call self.index file to index the file and save the data
                self.index_file(
                    full_path, 
                    index,
                    verbose=verbose
                )
                
        # Save the index
        faiss.write_index(index, self.index_bin_path)
        print_log('SUCCESS', 'FilesystemIndexer.index_filesystem()', f'FAISS index saved to "{self.index_bin_path}"') 
                
    
    def index_file(self, filepath:str, index:faiss.IndexFlatL2, verbose:bool=False) -> None: 
        """Reads the file at the given path, extracts the metadata and other info, hashes the file, and stores the results in the
        given sql DB using the connection and cursor, and stores the embedding in the given index.
        
            Parameters: 
                filepath (str): path to the file to index.
                cxn (sql.Connection): connection to an SQLite DB to store metadata.
                cursor (sql.Cursor): cursor for the SQLite DB.
                index (faiss.IndexFlatL2): a Faiss index to store embeddings.
                verbose (bool, optional): optionally print logs. 
                
            Returns: 
                None: saves the metadata in the SQLite DB and the embeddings in the index.
        """
        
        # Check the file extension and ignore invalid files
        if not filepath.endswith(('.pdf', '.docx', '.txt')): 
            
            # Info print and do not index the file
            if verbose: print_log('INFO', 'index_file()', f'Ignoring file (invalid extension) "{filepath}".')
            return  

        try:
            # Hash the file 
            file_hash:str = hash_file_sha256(filepath)

            # Check if this file exists in the DB already
            existing_entry:dict = self.file_metadata_db.check_file_exists(filepath)

            # Handle result
            if existing_entry: 

                # Check if the hashes match
                if file_hash == existing_entry['file_sha256']: 
                    
                    # Info print and do not index the file
                    if verbose: print_log('INFO', 'FilesystemIndexer.index_file()', f'ignoring "{filepath}" since it already exists with the same hash.')
                    return  

                # If hashes do not match, delete the existing entry so we can make a new one
                else:
                    
                    # Info print 
                    if verbose: print_log('INFO', 'FilesystemIndexer.index_file()', f'File "{filepath}" already exists in the database but with a different hash - updating DB entry.')
                    
                    # Delete existing row
                    self.file_metadata_db.delete_file_entry(filepath)
                    
            # Extract the metadata, text, and embedding for this file
            metadata:dict[str, str|int] = extract_metadata(filepath)
            file_text:str = read_file(filepath)
            embedding:int = self.sentence_transformer.encode(file_text)

            # Check the embedding 
            if embedding is None or len(embedding) != self.embedding_dim:
                
                # Info print (warn) and do nothing else 
                print_log('WARN', 'FilesystemIndexer.index_file()', f'Failed to generate valid embedding for "{filepath}". Skipping.')
                return 
            
            # Convert the embedding to an array and add to the index
            embedding_array:np.ndarray = np.array(embedding, dtype=np.float32).reshape(1, -1)
            index.add(embedding_array)

            # Insert the metadata for this file into the DB
            self.file_metadata_db.new_file_entry(
                filepath,
                os.path.basename(filepath),
                metadata,
                file_hash,
                embedding
            )

        # Handle exceptions
        except Exception as e:
            print_log('ERROR', 'FilesystemIndexer.index_file()', f"Error processing {filepath}. Caught exception: {e.__class__} - {e}")
            
            
    def search_files(self, query:str, top_k:int=5) -> list[int]:
        """Searches the index for the given query and returns the top_k matched file IDs."""

        # If the index filepath doesn't exist, then we cannot search, so return empty list
        if not os.path.exists(self.index_bin_path): return []
        
        # Read the existing index 
        index:faiss.IndexFlatL2 = faiss.read_index(self.index_bin_path)
        
        # Encode the query into an embedding and convert to a np array
        query_embedding:np.ndarray = np.array(
            self.sentence_transformer.encode(query), 
            dtype=np.float32
        ).reshape(1, -1)

        # Check shape of the query embedding 
        if query_embedding.shape[1] != self.embedding_dim:
            print("\033[91mERROR in search_files(): \033[0mQuery embedding has incorrect dimensions. Aborting search.")
            return []

        # Search the index for the query embedding for the top_k documents 
        _, indices = index.search(query_embedding, top_k)

        # Return the matched indices
        return indices
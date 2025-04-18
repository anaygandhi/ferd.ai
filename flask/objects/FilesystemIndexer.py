import os 
import faiss 
import numpy as np 
import logging 

from sentence_transformers import SentenceTransformer 
from .FileMetadataDatabase import FileMetadataDatabase
from utils import print_log, extract_metadata, hash_file_sha256, read_file, setup_logger


class FilesystemIndexer: 
    
    start_dir:str                            # The top level (TL) dir that this indexer starts at
    file_metadata_db:FileMetadataDatabase    # DB connection wrapper
    index_bin_path:str                       # Path to the Faiss index binary file 
    embedding_dim:int                        # Embedding dimensions for the index
    sentence_transformer:SentenceTransformer # Sentence transformer model for indexing files
    logger:logging.Logger                    # Logger for saving robust logs
    
    
    def __init__(self, start_dir:str, metadata_db_path:str, index_bin_path:str, embedding_dim:int, log_filepath:str='logs/filesystem_indexer.log', thread_num:int=0): 
        self.start_dir = start_dir
        self.file_metadata_db = FileMetadataDatabase(metadata_db_path)
        self.index_bin_path = index_bin_path
        self.embedding_dim = embedding_dim
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')  
        
        # Set up a logger for the FilesystemIndexer
        self.logger = setup_logger(
            log_filepath,
            f'filesystem_indexer_{thread_num}'
        )
        
        # Initial log that the indexer was init'd
        self.logger.debug(f'in __init__() - FilesystemIndexer initialized with [start_dir] = "{start_dir}", [metadata_db_path] = "{metadata_db_path}", [index_bin_path] = "{index_bin_path}"')
        
    
    def index_filesystem(self, overwrite:bool=False, verbose:bool=False, save_frequency:int=2) -> None: 
        """Indexes the filesystem starting at [self.start_dir] and recursively traverses child directories. 
        
            Parameters: 
                overwrite (bool, optional): "True" means that if the index & DB exist already then they will be overwritten from scratch; "False" means that only changed files
                    will be updated (i.e. where the stored hash does not match the computed hash). If the index does not exist, then it will be created in either case. Defaults to False. 
                verbose (bool, optional): "True" means print debug info; "False" means silent run and print only fatal errors. Defaults to False. 
                save_frequency (int, optional): the frequency to save the index. Must be one of [1, 2, 3], where: 
                    1 => save at the end only (after all dirs are indexed)
                    2 (default) => save after each directory iteration (each time a new directory is entered)
                    3 => save after each file is indexed (every time a new file is read - can be overkill and impact performance)
                    
            Returns: 
                None: updates/creates the faiss index and db at [self.index_bin_path] and [self.metadata_db_path] respectively. 
        """
        
        # ---- Setup ---- #
        # Create the dirs for the index bin if it doesn't exist
        os.makedirs(os.path.dirname(self.index_bin_path), exist_ok=True)
        
        # Check if overwriting existing data 
        if overwrite: 
            
            # Info print & log
            if verbose: print_log('WARN', 'index_filesystem()', f'Overwriting existing index at "{self.index_bin_path}".')
            self.logger.warning(f'in index_filesystem() - overwritting existing index at "{self.index_bin_path}".')
            
            # Delete the existing index 
            if os.path.exists(self.index_bin_path): os.remove(self.index_bin_path)
            
            # Create the index 
            index:faiss.IndexFlatL2 = faiss.IndexFlatL2(self.embedding_dim)
        
        # If NOT overwriting, then just make the SQL connection and read the existing index
        else: 
            
            # Info print & log
            if verbose: print_log('INFO', 'index_filesystem()', f'Reading existing index at "{self.index_bin_path}".')
            self.logger.info(f'in index_filesystem() - reading existing index at "{self.index_bin_path}".')
            
            # Read the existing index or create it if it doesn't exist
            if os.path.exists(self.index_bin_path): index:faiss.IndexFlatL2 = faiss.read_index(self.index_bin_path)
            else: index:faiss.IndexFlatL2 = faiss.IndexFlatL2(self.embedding_dim)
            
        # ---- Indexing ---- #
        # Info print & log
        if verbose: print_log('INFO', 'Filesystem.index_filesystem()', f'Starting indexing from "{self.start_dir}". Files: {os.listdir(self.start_dir)}')
        self.logger.info(f'in index_filesystem() - starting indexing from "{self.start_dir}"')
        
        # Iterate over all the child dirs in [self.start_dir] and recursively index each file
        for root, dirs, files in os.walk(self.start_dir):
            
            # Check if this dir is ignored 
            if self.file_metadata_db.check_path_ignored(root): 
                
                # Info print & log and do nothing else 
                if verbose: print_log('INFO', 'FilesystemIndexer.index_filesystem()', f'Skipping directory "{root}" because the path is ignored in DB.')
                self.logger.info(f'in index_filesystem() - skipping directory "{root}" because the path is ignored in DB.')
                continue 
            
            # Info print & log
            if verbose: print_log('INFO', 'FilesystemIndexer.index_filesystem()', f'Reading {len(files)} from {root}.')
            self.logger.info(f'in index_filesystem() - reading {len(files)} from {root}.')
            
            # Iterate over all the files in this dir
            for file in files:
                
                # Check the file extension and ignore invalid files
                if not file.endswith(('.pdf', '.docx', '.txt')): 
                    
                    # Info print & log and do not index the file
                    if verbose: print_log('INFO', 'index_filesystem()', f'Ignoring file (invalid extension) "{file}".')
                    self.logger.info(f'in index_filesystem() - ignoring file (invalid extension) "{file}".')
                    continue  
        
                # Construct the full filepath
                full_path = os.path.join(root, file)

                # Call self.index file to index the file and save the data
                self.index_file(
                    full_path, 
                    index,
                    verbose=verbose
                )
                
                # Save after file index if configured (level 3)
                if save_frequency == 3: 
                    faiss.write_index(index, self.index_bin_path)
                    
                    # Info print & log
                    if verbose: print_log('SUCCESS', 'FilesystemIndexer.index_filesystem()', f'FAISS index saved to "{self.index_bin_path}"') 
                    self.logger.info(f'in index_filesystem() - FAISS index saved to "{self.index_bin_path}" (save_frequency = 3)')
                    
            # Save after dir index if configured (level 2) 
            if save_frequency == 2: 
                faiss.write_index(index, self.index_bin_path)
                if verbose: print_log('SUCCESS', 'FilesystemIndexer.index_filesystem()', f'FAISS index saved to "{self.index_bin_path}"') 
                self.logger.info(f'in index_filesystem() - FAISS index saved to "{self.index_bin_path}" (save_frequency = 2)')
            
        # ALWAYS save after filesystem is indexed (level 1) 
        faiss.write_index(index, self.index_bin_path)
        if verbose: print_log('SUCCESS', 'FilesystemIndexer.index_filesystem()', f'FAISS index saved to "{self.index_bin_path}"') 
        self.logger.info(f'in index_filesystem() - FAISS index saved to "{self.index_bin_path}" (save_frequency = 1)')
        
            
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

        try:
            
            # Check if this path is ignored 
            if self.file_metadata_db.check_path_ignored(filepath): 
                
                # Info print 
                if verbose: print_log('INFO', 'index_file()', f'Ignoring file (path ignored in DB) "{filepath}".')
                self.logger.info(f'in index_file() - ignoring file (path ignored in DB) "{filepath}".')
                
                # Do nothing else 
                return  
            
            # Hash the file 
            file_hash:str = hash_file_sha256(filepath)

            # Check if this file exists in the DB already
            existing_entry:dict = self.file_metadata_db.check_file_exists(filepath)

            # Handle result
            if existing_entry: 

                # Check if the hashes match
                if file_hash == existing_entry['file_sha256']: 
                    
                    # Info print & log and do not index the file
                    if verbose: print_log('INFO', 'FilesystemIndexer.index_file()', f'ignoring "{filepath}" since it already exists with the same hash.')
                    self.logger.info(f'ignoring "{filepath}" since it already exists with the same hash.')
                    return  

                # If hashes do not match, delete the existing entry so we can make a new one
                else:
                    
                    # Info print 
                    if verbose: print_log('INFO', 'FilesystemIndexer.index_file()', f'File "{filepath}" already exists in the database but with a different hash - updating DB entry.')
                    self.logger.info(f'in index_file() - "{filepath}" already exists in the database but with a different hash - updating DB entry.')
                    
                    # Delete existing row
                    self.file_metadata_db.delete_file_entry(filepath)
                    
            # Extract the metadata, text, and embedding for this file
            metadata:dict[str, str|int] = extract_metadata(filepath)
            file_text:str = read_file(filepath)
            embedding:int = self.sentence_transformer.encode(file_text)

            # Check the embedding 
            if embedding is None or len(embedding) != self.embedding_dim:
                
                # Info print & log (warn) and do nothing else 
                if verbose: print_log('WARN', 'FilesystemIndexer.index_file()', f'Failed to generate valid embedding for "{filepath}". Skipping.')
                self.logger.warning(f'in index_file() - failed to generate valid embedding for "{filepath}". Skipping.')
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
            if verbose: print_log('ERROR', 'FilesystemIndexer.index_file()', f"Error processing {filepath}. Caught exception: {e.__class__} - {e}")
            self.logger.error(f'in index_file() - error processing {filepath}. Caught exception: {e.__class__} - {e}')
            
            
    def search_files(self, query:str, top_k:int=5) -> list[int]:
        """Searches the index for the given query and returns the top_k matched file IDs."""

        # Log
        self.logger.info(f'in search_files() - starting search in index for query: "{query}".')
        
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
            print_log('ERROR', 'FilesystemIndexer.search_files()', "Query embedding has incorrect dimensions. Aborting search.")
            self.logger.error('in search_files() - query embedding has incorrect dimensions. Aborting search.')
            return []

        # Search the index for the query embedding for the top_k documents 
        _, indices = index.search(query_embedding, top_k)
        
        # Log
        self.logger.info(f'in search_files() - search for "{query}" completed with matched file IDs: {indices}.')
        
        # Return the matched indices
        return list([int(i) for i in indices[0]])
    

    def search_subset(self, query:str, file_ids_to_include:list[int], top_k:int=5) -> list[int]:
        """Searches the index for the query, only considering the given subset of file IDs."""
        
        # Log
        self.logger.info(f'in search_subset() - searching index for "{query}" with {len(file_ids_to_include)} given IDs to include.')
        
        # If the index filepath doesn't exist OR if no file_ids_to_include are given, 
        # then we cannot search, so return empty list
        if (
            not os.path.exists(self.index_bin_path) or 
            not file_ids_to_include
        ): return []

        # Read the existing faiss index
        full_index:faiss.IndexFlatL2 = faiss.read_index(self.index_bin_path)

        # Init query embedding
        query_embedding = np.array(
            self.sentence_transformer.encode(query),
            dtype=np.float32
        ).reshape(1, -1)

        # Extract subset of vectors
        all_vectors:list = full_index.reconstruct_n(0, full_index.ntotal)
        subset_vectors:list = all_vectors[file_ids_to_include]

        # Create a temporary index with just the subset
        temp_index = faiss.IndexFlatL2(self.embedding_dim)
        temp_index.add(subset_vectors)

        # Search the index
        _, temp_indices = temp_index.search(query_embedding, top_k)

        # Map temporary indices back to real file IDs 
        matched_file_ids:list[int] = [file_ids_to_include[i] for i in temp_indices[0]]
        
        # Log
        self.logger.info(f'in search_subset() - completed search for "{query}" and got results: {matched_file_ids}.')
        
        # Return the real file IDs
        return matched_file_ids
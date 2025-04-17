from tqdm import tqdm 
import os 
import numpy as np 
import faiss
import sqlite3 as sql
import datetime as dt

from .metadata_extraction_utils import extract_metadata
from .text_extraction_utils import read_file
from .general import now, hash_file_sha256


def index_filesystem(start:str, model:object, cxn:sql.Connection, cursor:sql.Cursor, embedding_dim:int, index_path:str, index:faiss.IndexFlatL2, verbose:bool=False): 
    """Recursively indexes the files starting at the given [start] point and traverses each child directory."""

    print('STARTING FROM ', start)
    
    # Start with the given [start] dir
    for root, dirs, files in os.walk(start):

        # Info print
        if verbose: print(f'\n\033[0m[{now()}] \033[93mTraversing directory ("{root}").\n')

        # Do the files in this directory first 
        for filename in files:

            # Construct the whole file path
            filepath:str = os.path.join(root, filename)

            try: 
                # Check the file extension and ignore invalid files
                if not filename.endswith(('.pdf', '.docx', '.txt')): 
                    if verbose: print(f'\033[0m[{now()}] \033[90mINFO: \033[0mskipping "{filepath}" because it is not a supported extension.')
                    continue 

                # Hash the file 
                file_hash:str = hash_file_sha256(filepath)

                # Check if this file exists in the DB already
                cursor.execute('SELECT file_path, file_sha256 FROM file_metadata WHERE file_path = ?', (filepath,))

                # Get the result 
                db_filepath, db_hash = cursor.fetchone()

                # Handle result
                if db_filepath: 

                    # Check if the hashes match
                    if file_hash == db_hash: 
                        print(f'\033[0m[{now()}] \033[90mINFO: \033[0mignoring "{filepath}" since it already exists with the same hash.')
                        continue 

                    # If hashes do not match, reindex the file
                    else: 
                        print(f'\033[0m[{now()}] \033[90mINFO: \033[0mFile "{filepath}" already exists in the database but with a different hash - updating DB entry.')
                        
                        # Delete the existing row in the db 
                        cursor.execute("DELETE FROM file_metadata WHERE file_path == %s", (filepath,))
                        cxn.commit()

                # Extract the metadata, text, and embedding for this file
                metadata:dict[str, str|int] = extract_metadata(filepath)
                file_text:str = read_file(filepath)
                embedding:int = model.encode(file_text)

                # Check the embedding 
                if embedding is None or len(embedding) != embedding_dim:
                    print(f"\033[0m[{now()}] \033[93mWARN in index_directory(): \033[0mFailed to generate valid embedding for {filepath}. Skipping.")
                    continue
                
                # Convert the embedding to an array and add to the index
                embedding_array:np.ndarray = np.array(embedding, dtype=np.float32).reshape(1, -1)
                index.add(embedding_array)

                # Insert the metadata for this file into the DB
                cursor.execute(
                    '''
                        INSERT INTO file_metadata (file_path, file_name, file_size, file_sha256, created, modified, embedding)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', 
                    (
                        filepath,
                        filename,
                        metadata.get('file_size', 0),
                        file_hash,
                        metadata.get('created', ''),
                        metadata.get('modified', ''),
                        embedding_array.tobytes()
                    )
                )

                # Commit changes
                cxn.commit()

            # Handle exceptions
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

        # Now iterate over the directories 
        for dir in dirs: 
            index_directory(dir)


    # Save the index
    faiss.write_index(index, index_path)
    print("\033[92mSUCCESS: \033[0mFAISS index saved.")


def index_directory(directory_path:str, model:object, cxn:sql.Connection, cursor:sql.Cursor, embedding_dim:int, index_path:str, index:faiss.IndexFlatL2, verbose:bool=False) -> None:
    """Indexes the files in the given directory into the given index and resaves the index at the given index_path."""

    # Iterate over the given directory
    for root, dirs, files in os.walk(directory_path):

        # Info print
        if verbose: print(f'\n\033[0m[{now()}] \033[93mTraversing directory ("{root}").\n')

        # Iterate over all the files in the current directory 
        for file in tqdm(files, total=len(files), desc=f'Indexing files'):
            
            # Check the file extension and ignore invalid files
            if not file.endswith(('.pdf', '.docx', '.txt')): continue 

            # Construct the path to this file
            file_path:str = os.path.join(root, file)

            try:
                # Check if this file exists in the DB already
                cursor.execute('SELECT COUNT(*) FROM file_metadata WHERE file_path = ?', (file_path,))

                # Handle result
                if cursor.fetchone()[0] > 0:
                    print(f"\033[93mNOTICE in index_directory(): \033[0mFile {file_path} already exists in the database. Skipping insertion.")
                    continue
                
                # Extract the metadata, text, and embedding for this file
                metadata:dict[str, str|int] = extract_metadata(file_path)
                file_text:str = read_file(file_path)
                embedding:int = model.encode(file_text)

                # Check the embedding 
                if embedding is None or len(embedding) != embedding_dim:
                    print(f"\033[93mNOTICE in index_directory(): \033[0mFailed to generate valid embedding for {file_path}. Skipping.")
                    continue
                
                # Convert the embedding to an array and add to the index
                embedding_array:np.ndarray = np.array(embedding, dtype=np.float32).reshape(1, -1)
                index.add(embedding_array)

                # Insert the metadata for this file into the DB
                cursor.execute(
                    '''
                        INSERT INTO file_metadata (file_path, file_name, file_size, created, modified, embedding)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', 
                    (
                        file_path,
                        os.path.basename(file_path),
                        metadata.get('file_size', 0),
                        metadata.get('created', ''),
                        metadata.get('modified', ''),
                        embedding_array.tobytes()
                    )
                )

                # Commit changes
                cxn.commit()

            # Handle exceptions
            except Exception as e:
                print(f"Error processing {file_path}: {e}")


def search_files(query:str, model, embedding_dim:int, index:faiss.IndexFlatL2, cursor:sql.Cursor, top_k:int=5):
    """Searches the given index for the given query, using the given model to create an embedding for the query, and returns 
    the top_k matched filenames."""

    # Encode the query into an embedding and convert to a np array
    query_embedding:np.ndarray = np.array(model.encode(query), dtype=np.float32).reshape(1, -1)

    # Check shape of the query embedding 
    if query_embedding.shape[1] != embedding_dim:
        print("\033[91mERROR in search_files(): \033[0mQuery embedding has incorrect dimensions. Aborting search.")
        return []

    # Search the index for the query embedding for the top_k documents 
    _, indices = index.search(query_embedding, top_k)

    # Init an array of filenames to return
    file_names:list[str] = []

    # Iterate over the index matches and save the filenames
    for idx in indices[0]:

        # Check if valid index
        if idx != -1:

            # Get the filename for this index 
            cursor.execute(f"SELECT file_name FROM file_metadata WHERE id = {idx + 1}")
            result = cursor.fetchone()

            # Add result to the list of file names if it exists
            if result: file_names.append(result[0])

    # Return the populated list of filenames 
    return file_names
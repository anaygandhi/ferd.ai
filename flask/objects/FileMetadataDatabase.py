
import os
import sqlite3 as sql
import numpy as np 
import pandas as pd 
import logging 

from utils import normalize_path, setup_logger


class FileMetadataDatabase: 
    
    db_path:str                 # Path to the DB file
    cxn:sql.Connection          # Connection to the db
    cursor:sql.Cursor           # Cursor for the db
    create_tables_script:str    # Path to the sql script to create the tables for the db
    logger:logging.Logger       # Logger for the DB
        
    
    def __init__(self, db_path:str, create_tables_script:str='sql/metadata_db_tables.sql', log_filepath:str='logs/file_metadata_database.log', thread_num:int=0): 
        self.db_path = db_path
        self.logger = setup_logger(log_filepath, f'file_metadata_db_{thread_num}')    
           
        # If the db already exists, make a cxn and cursor
        if os.path.exists(db_path): 
            self.cxn = sql.connect(db_path)
            self.cursor = self.cxn.cursor()
            
            # Log 
            self.logger.info(f'in __init__() - initialized connection to existing database at "{db_path}"')
        
        # If the db doesn't exist, create it and create the tables 
        else: 
            # Create the dir if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Connection and cursor 
            self.cxn = sql.connect(db_path)
            self.cursor = self.cxn.cursor() 
            
            # Execute the create tables script
            with open(create_tables_script, 'r') as file: 
                self.cursor.executescript(file.read())
                
            # Commit changes
            self.cxn.commit()
            
            # Log
            self.logger.info(f'in __init__() - created a new database file at "{db_path}"')
                    
    
    # --- Funcs relating to the "file_metadata" table --- # 
    def check_file_exists(self, filepath:str) -> dict|None: 
        """Checks if the given filepath exists in the DB's "file_metadata" table, and returns that row as a dict if it does.""" 
        
        # Log
        self.logger.info(f'in check_file_exists() - checking for file path "{filepath}"')
        
        # Execute SELECT query for the given filepath
        self.cursor.execute('SELECT * FROM file_metadata WHERE file_path = ?', (filepath,)) 
        
        # Check result
        result:tuple = self.cursor.fetchone()
        
        # Process result and return
        # GOT result 
        if result: 
            
            # Log result and return 
            self.logger.info(f'in check_file_exists() - got result: {result}')
            
            return {
                col : val 
                for col,val in zip(self.get_table_columns('file_metadata'), result)
            }    
            
        # NO result
        else:
            self.logger.info(f'in check_file_exists() - no results found for "{filepath}"') 
            return None
        
    
    def delete_file_entry(self, filepath:str) -> None: 
        """Deletes the entry for the given filepath from the "file_metadata" table."""
                
        # Execute query
        self.logger.info(f'in delete_file_entry() - deleting metadata entry for "{filepath}"')
        self.cursor.execute("DELETE FROM file_metadata WHERE file_path == %s", (filepath,))
        
        # Commit changes
        self.cxn.commit()
        self.logger.info(f'in delete_file_entry() - transaction completed for "{filepath}"')
        
           
    def new_file_entry(self, filepath:str, filename:str, metadata:dict, file_hash:str, embedding_array:np.ndarray) -> None: 
        """Creates a new row in the "file_metadata" table with the given information."""
        
        # Log
        self.logger.info(f'in new_file_entry() - creating a new entry for "{filepath}"')
        
        # Normalize the filepath 
        filepath = normalize_path(filepath)
        
        # Execute INSERT query
        self.cursor.execute(
            '''
                INSERT INTO file_metadata (file_path, file_name, file_size, file_sha256, created, modified, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
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
        self.logger.info(f'in new_file_entry() - transaction completed for new entry "{filepath}"')
        self.cxn.commit()
        
    
    def file_paths_from_ids(self, ids:list[int]) -> list[str]: 
        """Returns the paths for the files with the given IDs, while preserving the order of the passed IDs."""
        
        # Log
        self.logger.info(f'in file_paths_from_ids() - retrieving paths for {len(ids)} IDs.')
        
        # Check that IDs are actually given
        if len(ids) == 0: 
            self.logger.warning('in file_paths_from_ids() - not given any IDs (len == 0).')
            return []
        
        # Construct the VALUES clause for the query
        values_clause:str = ','.join('(?, ?)' for _ in ids)
        
       # Flatten (id, index) pairs for parameters
        params:list[int] = [item for pair in zip(ids, range(len(ids))) for item in pair] 

        # Construct the query
        query = f"""
            WITH input_order(id, ord) AS (
                VALUES {values_clause}
            )
            SELECT io.ord, fmd.file_path
            FROM input_order io
            LEFT JOIN file_metadata fmd ON fmd.id = io.id
            ORDER BY io.ord
        """
        
        # Execute the query
        self.cursor.execute(query, params)
        
        # Fetch results
        rows:list[tuple] = self.cursor.fetchall()
        
        # NOTE: Since we SELECT ord, we can reconstruct the full list with None for missing paths
        # Init a list of all None vals to hold the results
        result:list[str|None] = [None] * len(ids)
        
        # Iterate over each of the result tuples (in order) and insert the path for each index
        for ord_index, file_path in rows:
            result[ord_index] = file_path

        # Return the resulting list of strings
        self.logger.info(f'in file_paths_from_ids() - transaction for {len(ids)} completed.')
        return result

    
    def get_file_ids_by_path_prefix(self, top_level_path: str) -> list[int]:
        """Returns the IDs of all files that are downstream from the given top level path."""
        
        # Log 
        self.logger.info(f'in get_file_ids_by_path_prefix() - retrieving the IDs for files relative to "{top_level_path}"')
        
        # Ensure the path ends with a separator so it's not just a prefix match
        path_prefix:str = top_level_path.rstrip(os.sep) + os.sep + '%'

        # Execute the query
        self.cursor.execute(
            "SELECT id FROM file_metadata WHERE file_path LIKE ?", 
            (path_prefix,)
        )
        
        # Fetch results and return 
        results:list[int] = [row[0] for row in self.cursor.fetchall()]
        
        self.logger.info(f'in get_file_ids_by_path_prefix() - got {len(results)} results for top level directory "{top_level_path}"')
        return 


    # --- Funcs relating to the "ignore_paths" table --- #     
    def new_ignored_path(self, path:str, type:str) -> None: 
        """Creates a new entry in the "ignored_paths" table for the given path."""
        
        # Log
        self.logger.info(f'in new_ignored_path() - creating a new entry for "{path}" (type = "{type}")')
        
        # Convert the given type to lowercase 
        type = type.lower()
        
        # Check that a valid type is given    
        if not type in ['file', 'directory']: raise AttributeError(f'Given type "{type}" is not valid. Must be one of "file" or "directory".')
        
        # Normalize the path format 
        path = normalize_path(path) 
        
        try: 
            # Insert the new row
            self.cursor.execute(
                'INSERT INTO ignore_paths(path, type) VALUES(?, ?)',
                (path, type)
            )
            
            # Commit changes 
            self.logger.info(f'in new_ignored_path() - transaction for "{path}" completed successfully.')
            self.cxn.commit() 

            
        # Handle exceptions
        except sql.IntegrityError: 
            # Integrity error means the path is already ignored - do nothing
            self.logger.warning(f'in new_ignored_path() - given path "{path}" is already ignored.')
            return 
        
        
    def check_path_ignored(self, path:str) -> bool: 
        """Checks if the given path is ignored. NOTE: the path must actually exist in the filesystem and should be an absolute path."""
        
        # Log
        self.logger.info(f'in check_path_ignored() - checking for "{path}"')
        
        # Normalize the path 
        path = normalize_path(path) 
                
        # Make sure the path exists, return False if not
        if not os.path.exists(path): return False
                
        # Check if the path is a file or directory to optimize the query
        if os.path.isdir(path): 
            t:str = 'directory'
        else: 
            t:str = 'file'
                
        # Execute select query
        self.cursor.execute(
            "SELECT 1 FROM ignore_paths WHERE type = ? AND ? GLOB path LIMIT 1", 
            (t, path)
        )
        
        # Fetch results
        result:int = self.cursor.fetchone()
                
        # Check if we got a direct match
        if result and result[0] > 0: 
            self.logger.info(f'in check_path_ignored() - "{path}" is ignored (directly).')
            return True    
        
        # If no direct match and it is a file, check if it is in an ignored directory
        elif t == 'file': 
            
            # Get the parent dir
            parent:str = os.path.dirname(path)
            
            # Traverse backwards down the path and keep checking if the parent dir is ignored
            while parent and parent != '/':
                
                # Normalize the path 
                parent = normalize_path(parent)
                
                # Execute query
                self.cursor.execute(
                    "SELECT 1 FROM ignore_paths WHERE type = 'directory' AND ? GLOB path LIMIT 1",
                    (parent,)
                )
                
                # Return true if there is a result (i.e. this parent is ignored)                
                if self.cursor.fetchone(): 
                    self.logger.info(f'in check_path_ignored() - "{path}" is ignored (inheritence from "{parent}")')
                    return True
                
                # If no match, get the parent dir of this dir
                new_parent:str = os.path.dirname(parent)
                
                # Prevent infinite loop at root
                if new_parent == parent: break
                
                # Set the parent as the new parent  
                parent = new_parent

        # False if we make it here
        self.logger.info(f'in check_path_ignored() - "{path}" is not ignored.')
        return False
    
        
    def get_ignored_files_in_dir(self, dir_path:str) -> list[str]: 
        """Returns the filepaths for files in the given dir that are ignored."""
        
        # Log
        self.logger.info(f'in get_ignored_files_in_dir() - getting ignored files from the top level directory "{dir_path}"')
        
        # If the dir path does not include a wildcard at the end, then add it
        if not dir_path.endswith('/*'): 
            dir_path = dir_path.rstrip('/\\') + '/*'
        
        # Execute the query
        self.cursor.execute(
            """
                SELECT path 
                FROM ignore_paths 
                WHERE type = ?
                AND path GLOB ?
            """,
            ('file', dir_path)
        )
        
        # Fetch results and return
        results:list[str] = [r[0] for r in self.cursor.fetchall()]
        
        self.logger.info(f'in get_ignored_files_in_dir() - got {len(results)} for directory "{dir_path}"')
        return results
    
    
    def get_all_ignored_paths(self) -> list[str]: 
        """Returns all the ignored directories and files in the ignore_paths table and returns the results as a list of 
        dicts, where each dict is like: {'path': '<ignored_path>', 'type': '<file|directory>'."""
        
        # Use the table_as_df util to get the ignored_paths table as a df, orient to a list of dict, and return
        return self.table_as_df('ignored_paths').to_dict(orient='records')
    
    
    def del_ignored_path(self, path:str) -> None: 
        """Deletes the given path from the "ignored_paths" database if it exists."""
        
        # Log
        self.logger.info(f'in del_ignored_path() - deleting entry for "{path}" (if it exists).')
        
        # Execute query
        self.cursor.execute(
            "DELETE FROM ignored_paths WHERE path = ?",
            (path,)
        )

        # Commit changes
        self.cxn.commit()
        self.logger.info(f'in del_ignored_path() - transaction to delete "{path}" completed successfully.')
        
        
    # --- Other utils --- #
    def table_as_df(self, table_name:str) -> pd.DataFrame: 
        """Returns the given table as a DataFrame."""
        
        # Execute select query for the table
        self.cursor.execute(f'SELECT * FROM {table_name}')
        
        # Fetch all results and create a df, and return
        return pd.DataFrame(
            self.cursor.fetchall(),
            columns=self.get_table_columns(table_name)
        )
    
    
    def get_table_columns(self, table_name:str) -> list[str]: 
        """Returns the columns for the given table name."""
        
        # Execute query
        self.cursor.execute(f'PRAGMA table_info({table_name})')
        
        # Return results
        return [c[1] for c in self.cursor.fetchall()]
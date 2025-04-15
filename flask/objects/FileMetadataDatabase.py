
import os
import sqlite3 as sql
import numpy as np 
import pandas as pd 


class FileMetadataDatabase: 
    
    db_path:str                 # Path to the DB file
    cxn:sql.Connection          # Connection to the db
    cursor:sql.Cursor           # Cursor for the db
    create_tables_script:str    # Path to the sql script to create the tables for the db
    
    
    def __init__(self, db_path:str, create_tables_script:str='sql/metadata_db_tables.sql'): 
        self.db_path = db_path
        
        # If the db already exists, make a cxn and cursor
        if os.path.exists(db_path): 
            self.cxn = sql.connect(db_path)
            self.cursor = self.cxn.cursor()
            
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
                
    
    def get_table_columns(self, table_name:str) -> list[str]: 
        """Returns the columns for the given table name."""
        
        # Execute query
        self.cursor.execute(f'PRAGMA table_info({table_name})')
        
        # Return results
        return [c[1] for c in self.cursor.fetchall()]
    
        
    def check_file_exists(self, filepath:str) -> dict|None: 
        """Checks if the given filepath exists in the DB's "file_metadata" table, and returns that row as a dict if it does.""" 
            
        # Execute SELECT query for the given filepath
        self.cursor.execute('SELECT * FROM file_metadata WHERE file_path = ?', (filepath,)) 
        
        # Check result
        result:tuple = self.cursor.fetchone()
        
        # Process result and return
        # GOT result 
        if result: 
            return {
                col : val 
                for col,val in zip(self.get_table_columns('file_metadata'), result)
            }    
            
        # NO result
        else: 
            return None
        
    
    def delete_file_entry(self, filepath:str) -> None: 
        """Deletes the entry for the given filepath from the "file_metadata" table."""
        
        # Execute query
        self.cursor.execute("DELETE FROM file_metadata WHERE file_path == %s", (filepath,))
        
        # Commit changes
        self.cxn.commit()
        
        
    def new_file_entry(self, filepath:str, filename:str, metadata:dict, file_hash:str, embedding_array:np.ndarray) -> None: 
        """Creates a new row in the "file_metadata" table with the given information."""
        
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
        self.cxn.commit()
        
        
    def table_as_df(self, table_name:str) -> pd.DataFrame: 
        """Returns the given table as a DataFrame."""
        
        # Execute select query for the table
        self.cursor.execute(f'SELECT * FROM {table_name}')
        
        # Fetch all results and create a df, and return
        return pd.DataFrame(
            self.cursor.fetchall(),
            columns=self.get_table_columns(table_name)
        )
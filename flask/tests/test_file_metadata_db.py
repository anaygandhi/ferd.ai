
import pytest
from configparser import ConfigParser

# Modify sys path for util and obj imports 
import sys
import os

parent_dir:str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
# Finish imports 
from objects import FileMetadataDatabase 
from utils import normalize_path

 
# ---- Config ---- # 
# Define a path to a tmp db for testing
DB_FILEPATH:str = './file_metadata.db'

# Info print the cwd 
print(f'\n\033[93mRunning tests relative to working dir: \033[0m{os.getcwd()}\n')

# ---- Setup ---- # 
# Init a db connection
file_metadata_db:FileMetadataDatabase = FileMetadataDatabase(DB_FILEPATH, create_tables_script='../sql/metadata_db_tables.sql')

# Insert a file to be ignored explicitly
file_metadata_db.new_ignored_path(
    r'C:\Users\jjhea\OneDrive\Coding-Practice-and-Apps\ferd-ai\indexing-filesystem\test_pdfs\stm32f413rh.pdf',
    'file'
)

# Insert a directory to ignore
file_metadata_db.new_ignored_path(
    r'C:\Users\jjhea\OneDrive\Coding-Practice-and-Apps\ferd-ai\indexing-filesystem\test_pdfs\subdir1',
    'directory'
)

# Fixture for tests 
@pytest.fixture
def file_db():
    return file_metadata_db

# Define test vars
@pytest.mark.parametrize("input_path,expected", [
    
    # -- IGNORED paths -- # 
    # Relative paths (rel to "indexing-filesystem/flask/tests")
    (r"..\..\.git", True),                        # Hidden dir
    (r"..\..\test_pdfs\stm32f413rh.pdf", True),   # Ignored explicitly
    
    # Absolute paths 
    (r"C:\Users\jjhea\OneDrive\Coding-Practice-and-Apps\ferd-ai\indexing-filesystem\.git", True),                               # Hidden dir
    (r"C:\Users\jjhea\OneDrive\Coding-Practice-and-Apps\ferd-ai\indexing-filesystem\test_pdfs\stm32f413rh.pdf", True),          # Ignored explicitly
    (r"C:\Users\jjhea\OneDrive\Coding-Practice-and-Apps\ferd-ai\indexing-filesystem\test_pdfs\subdir1", True),                  # Ignored explicitly
    (r"C:\Users\jjhea\OneDrive\Coding-Practice-and-Apps\ferd-ai\indexing-filesystem\test_pdfs\subdir1\calcmolzon.pdf", True),   # Ignored by inheritence (via parent) 

    # -- NOT IGNORED paths -- # 
    # Relative paths
    (r"..\..\test_pdfs", False),                    
    
    # Absolute paths
    (r"C:\Users\jjhea\OneDrive\Coding-Practice-and-Apps\ferd-ai\indexing-filesystem", False)
])


# ---- Tests ---- #
def test_check_path_ignored(file_db, input_path, expected):
    result = file_db.check_path_ignored(input_path)
    assert result == expected

# NOTE: run this script from the "flask/" directory so paths work properly

from configparser import ConfigParser 
import threading as th 
import logging 
import time 

# Modify sys path for util imports 
import sys
import os

parent_dir:str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from objects import FilesystemIndexer
from utils import get_root_directories, setup_logger


# --- Config --- #
# Read config file
config:ConfigParser = ConfigParser() 
config.read('config/config.conf')

# Extract needed vars from config
METADATA_DB_PATH:str = config['paths']['METADATA_DB_PATH'] 
INDEX_BIN_PATH:str = config['paths']['INDEX_BIN_PATH']
EMBEDDING_DIM:int = int(config['index']['EMBEDDING_DIM'])
LOGS_DIR:str = config['paths']['LOGS_DIR']

# Define other vars
SLEEP_TIME:int = 5                 # Sleep time between print/log updates
all_threads:list[th.Thread] = []   # Array to hold all the threads 

# Init a logger for this script
logger:logging.Logger = setup_logger(
    os.path.join(LOGS_DIR, 'indexer_threads.log'),
    'indexer_threads_script_logger'
)


# --- Define func to init and start a FilesystemIndexer for each root dir --- # 
def init_and_run_indexer(root_dir:str, thread_num:int=0) -> None: 
    """Creates a FilesystemIndexer for the given root directory and starts indexing the downstream files and directories."""
    
    # Init an indexer 
    filesystem_indexer:FilesystemIndexer = FilesystemIndexer(
        root_dir,
        METADATA_DB_PATH,
        INDEX_BIN_PATH,
        EMBEDDING_DIM,
        log_filepath=os.path.join(LOGS_DIR, 'filesystem_indexer', f'filesystem_indexer_{thread_num}.log'),
        thread_num=thread_num
    ) 
    
    # Start indexing the filesystem from the given root dir
    filesystem_indexer.index_filesystem(
        overwrite=False,
        verbose=False,
        save_frequency=2,
    )
    
    
# --- Start threads for each of the root dirs --- #
# Keep track of the number of threads 
i:int = 0

# Get all the root dirs for this system
root_dirs:list[str] = get_root_directories() 

# Iterate over each of the root dirs and start threads 
for root_dir in root_dirs:
    
    # Create a thread 
    thread:th.Thread = th.Thread(
        name='FilesystemIndexer-Thread-' + str(i),
        target=init_and_run_indexer,
        args=(root_dir,),
        kwargs={
            'thread_num': i
        },
        
        # NOTE: daemon so the thread exists if the program is killed or crashes 
        daemon=True
    )
    
    # Add the thread to the list of all threads
    all_threads.append(thread)
    
    # Start the thread 
    logger.info(f'Starting thread for root dir "{root_dir}" ({i}/{len(root_dirs)})')
    thread.start()
    
    # Increment i
    i += 1

    
# --- Continual logging --- # 
# Sleep [SLEEP_TIME] between logs
num_threads:int = len(all_threads)  # Compute num threads to avoid recomputing every time

# Run until exception
run:bool = True     # Run flag 

try: 
    while run: 
        
        # Init counters
        num_alive:int = 0
        num_dead:int = 0
        alive_thread_names:list[str] = []
        dead_thread_names:list[str] = []
        # Get the status for all threads
        for t in all_threads: 
            if t.is_alive(): 
                alive_thread_names.append(t.name)
                num_alive += 1
            else: 
                dead_thread_names.append(t.name)
                num_dead += 1 
        
        # Log status
        logger.info(f'Number of threads (alive, dead): ({num_alive}, {num_dead}) out of {num_threads}')
        logger.info(f'Alive thread names: {alive_thread_names}')
        logger.info(f'Dead thread names: {dead_thread_names}')

        # Sleep 
        time.sleep(SLEEP_TIME) 
        
# Kill all threads 
except Exception as e: 
    
    # Log exception and quit the program
    logger.critical(f'Caught exception - {e.__class__}: {e}')
    logger.info('Exiting main thread. Daemon threads will terminate.')
    
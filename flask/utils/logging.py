import logging
import os

from .general import now 


def print_log(level:str, loc:str, msg:str) -> None: 
    """Prints the given message to the terminal with a timestamp and the given log level.
    
        Parameters: 
            level (str): level to print - accepted levels are: "INFO" (grey), "WARN" (yellow), "ERROR" (red), "SUCCESS" (green), "MISC" (blue).
            loc (str): the calling function so that the log is meaningful and can be traced.
            msg (str): message to print after the timestamp and level (appears in white).
            
        Returns: 
            None: prints the log to the terminal like: "[HH:MM:SS] {level} in {loc}: {msg}" 
    """
    # Convert level to uppercase
    level = level.upper()
    
    # Check that a valid level is given and set the color accordingly
    match level: 
        case 'INFO': color:str = '\033[90m'     # Grey
        case 'WARN': color:str = '\033[93m'     # Yellow
        case 'ERROR': color:str = '\033[91m'    # Red
        case 'MISC': color:str = '\033[94m'     # Blue
        case 'SUCCESS': color:str = '\033[92m'  # Green
        case _: color:str = '\033[94m'          # Default: Blue
    
    # Print the log
    print(f'\033[0m[{now()}] {color}{level} in {loc}: \033[0m{msg}')
    

def setup_logger(log_file_path:str, logger_name:str, min_level:int=logging.DEBUG, log_format:str='%(asctime)s - %(levelname)s: %(message)s') -> logging.Logger:
    """Sets up a logger to save logs to the given filepath."""
    
    # Init a logger and set the lowest level to DEBUG (so all logs are captured)
    logger:logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(min_level)
    
    # Prevent double logging if root logger is used
    logger.propagate = False  

    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        
        # Create the output dir if it doesn't exist
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        # Create a file handler
        file_handler:logging.FileHandler = logging.FileHandler(log_file_path, encoding='utf-8')
        logger.addHandler(file_handler)
        
        # Set the format for logs 
        formatter:logging.Formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        
    # Return the logger
    return logger

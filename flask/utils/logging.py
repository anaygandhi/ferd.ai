from .general import now 


def print_log(level:str, loc:str, msg:str) -> None: 
    """Prints the given message to the terminal with a timestamp and the given log level.
    
        Parameters: 
            level (str): level to print - accepted levels are: "INFO" (grey), "WARN" (yellow), "ERROR" (red), "MISC" (blue).
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
        case _: color:str = '\033[94m'          # Default: Blue
    
    # Print the log
    print(f'\033[0m[{now()}] {color}{level} in {loc}: \033[0m{msg}')
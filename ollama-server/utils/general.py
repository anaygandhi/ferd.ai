import re
import json
from hashlib import sha256
import platform 
import datetime as dt 


def now() -> str: 
    """Returns the current time as a string for printing."""
    return dt.datetime.now().strftime('%H:%M:%S')




def hash_file_sha256(path:str, chunk_size:int=8192) -> str:
    """Hashes the file at the given path"""

    # Init a hash func
    h = sha256()

    # Read the file in chunks and update the hash
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    
    # Return the hash as a string
    return h.hexdigest()


def extract_json(text: str) -> dict:
    """Extracts the first JSON object from a block of text using bracket counting."""

    start = text.find('{')
    if start == -1:
        return None

    count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            count += 1
        elif text[i] == '}':
            count -= 1

        if count == 0:
            try:
                return json.loads(text[start:i+1])
            except json.JSONDecodeError:
                return None
    return None


def get_root_directories():
    """Gets the mounted drives for the current OS."""

    # Get the current OS
    system = platform.system()

    # Act according to OS
    if system == "Windows":
        # On Windows, list all mounted drive letters
        import string
        from ctypes import windll

        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for i, letter in enumerate(string.ascii_uppercase):
            if bitmask & (1 << i):
                drives.append(f"{letter}:\\")
        return drives

    else:
        # On Unix/Linux/macOS, just return root
        return ['/']
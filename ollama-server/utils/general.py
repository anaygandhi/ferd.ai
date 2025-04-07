import re
import json
import platform 


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
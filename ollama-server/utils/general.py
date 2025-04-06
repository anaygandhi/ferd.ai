import re
import json

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
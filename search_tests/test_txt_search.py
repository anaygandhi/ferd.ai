import os
import sys
from docx import Document
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from file_content_extractions.text_extraction import search_in_txt

# Creating a test TXT file
def create_test_txt(filename="test.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("Hello, this is a test TXT file.")

# Testing TXT extraction functionality
def test_txt_functionality():
    test_txt = "test.txt"
    create_test_txt(test_txt)
    expected_text = "Hello, this is a test TXT file."
    
    if os.path.exists(test_txt):
        extracted_text = search_in_txt(test_txt).strip()
        print("\nExtracted Text from TXT:\n", extracted_text)

        if expected_text != extracted_text:
            print(f"Test Failed: Expected '{expected_text}', but got '{extracted_text}'")
        else:
            print("Test Passed: Extracted text matches expected content")

# Run  
if __name__ == "__main__":
    test_txt_functionality()

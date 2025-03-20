import os
import sys
from docx import Document
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from search import search_in_docx

# Creating a test docx file
def create_test_docx(filename="test.docx"):
    doc = Document()
    doc.add_paragraph("Hello, this is a test docx file.")
    doc.save(filename)

# Testing the docx search functionality
def test_docx_functionality():
    test_docx = "test.docx"
    create_test_docx(test_docx)
    expected_text = "Hello, this is a test docx file."
    
    if os.path.exists(test_docx):
        extracted_text = search_in_docx(test_docx).strip()
        print("\nExtracted Text from DOCX:\n", extracted_text)

        if expected_text not in extracted_text:
            print(f"Test Failed: Expected '{expected_text}', but got '{extracted_text}'")
        else:
            print("Test Passed: Extracted text matches expected content")
    else:
        print(f"Test Failed: {test_docx} not found")

# Run  
if __name__ == "__main__":
    test_docx_functionality()

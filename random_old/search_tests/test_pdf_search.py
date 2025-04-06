from fpdf import FPDF
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from file_content_extractions.text_extraction import search_in_pdf

# Creating a test PDF file
def create_test_pdf(filename="test.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hello, this is a test PDF.", ln=True, align='C')
    pdf.output(filename)

# Testing the PDF search functionality
def test_pdf_functionality():
    test_pdf = "test.pdf"
    create_test_pdf(test_pdf)
    expected_text = "Hello, this is a test PDF."
    
    if os.path.exists(test_pdf):
        extracted_text = search_in_pdf(test_pdf).strip()
        print("\nExtracted Text from PDF:\n", extracted_text)

        if expected_text not in extracted_text:
            print(f"Test Failed: Expected '{expected_text}', but got '{extracted_text}'")
        else:
            print("Test Passed: Extracted text matches expected content")
    else:
        print(f"Test Failed: {test_pdf} not found")

# Run  
if __name__ == "__main__":
    test_pdf_functionality()

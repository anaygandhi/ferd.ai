from fpdf import FPDF
import os
from pdf_search import search_in_pdf

# Creating a test PDF file
def create_test_pdf(filename="test.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hello, this is a test PDF.", ln=True, align='C')
    pdf.output(filename)
    print(f"{filename} has been created.")

# Testing the PDF search functionality
def test_pdf_functionality():
    test_pdf = "test.pdf"
    create_test_pdf(test_pdf)
    if os.path.exists(test_pdf):
        extracted_text = search_in_pdf(test_pdf)
        print("\nExtracted Text:\n", extracted_text)
        assert "Hello, this is a test PDF." in extracted_text, "Test Failed: Text does not match"
        print("Test Passed: Extracted text matches expected content")
    else:
        print(f"Test Failed: {test_pdf} not found")

# Run
if __name__ == "__main__":
    test_pdf_functionality()

import pymupdf
from docx import Document
import pytesseract
from pdf2image import convert_from_path
from PIL import Image 

# Extracting text from a PDF file
def search_in_pdf(file_path):
    doc = pymupdf.open(file_path)
    extracted_text = ""
    for page in doc:
        text = page.get_text()
        if text.strip():
            extracted_text += text + "\n"
        else:
            extracted_text += pdf_ocr_extraction(file_path) + "\n"
    return extracted_text.strip() 
    

# Extracting text from a scanned PDF file using OCR
def pdf_ocr_extraction(file_path):
    images = convert_from_path(file_path)  
    extracted_text = []

    for image in images:
        text = pytesseract.image_to_string(image)
        extracted_text.append(text)

    return "\n".join(extracted_text)


# Extracting text from a DOCX file
def search_in_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Extracting text from a TXT file
def search_in_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Main search in any file type 
def search_in_file(file_path):
    if file_path.endswith('.pdf'):
        return search_in_pdf(file_path)
    elif file_path.endswith('.docx'):
        return search_in_docx(file_path)
    elif file_path.endswith('.txt'):
        return search_in_txt(file_path)
    else:
        raise ValueError("Unsupported file format")
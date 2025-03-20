import fitz
from docx import Document


# Extracting text from a PDF file
def search_in_pdf(file_path):
    doc = fitz.open(file_path)
    return "".join([page.get_text() for page in doc])


# Extracting text from a .docx file
def search_in_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


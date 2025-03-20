import fitz
from docx import Document


# Extracting text from a PDF file
def search_in_pdf(file_path):
    doc = fitz.open(file_path)
    return "".join([page.get_text() for page in doc])


# Extracting text from a docx file
def search_in_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Extracting text from a txt file
def search_in_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Main searhc in any file type 
def search_in_file(file_path):
    if file_path.endswith('.pdf'):
        return search_in_pdf(file_path)
    elif file_path.endswith('.docx'):
        return search_in_docx(file_path)
    elif file_path.endswith('.txt'):
        return search_in_txt(file_path)
    else:
        raise ValueError("Unsupported file format")
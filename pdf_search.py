import fitz

# Extracting text from a PDF file
def search_in_pdf(file_path):
    doc = fitz.open(file_path)
    return "".join([page.get_text() for page in doc])


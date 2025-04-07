import pymupdf
from docx import Document
import pytesseract
from pdf2image import convert_from_path
from PIL import Image 


def read_pdf(file_path:str) -> str:
    """Extracts the text from the given PDF."""

    doc = pymupdf.open(file_path)
    extracted_text = ""
    for page in doc:
        text = page.get_text()
        if text.strip():
            extracted_text += text + "\n"
        else:
            extracted_text += read_pdf_imgs(file_path) + "\n"
    return extracted_text.strip() 
    

def read_pdf_imgs(file_path:str) -> str:
    """Converts the images from the given PDF into text."""

    images = convert_from_path(file_path)  
    extracted_text = []

    for image in images:
        text = pytesseract.image_to_string(image)
        extracted_text.append(text)

    return "\n".join(extracted_text)


def read_docx(file_path:str) -> str:
    """Extracts the text from the given docx."""

    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def read_txt(file_path:str) -> str:
    """Extracts the text from the given txt file."""

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_file(file_path:str) -> str:
    """Extracts the text from the given file."""

    # Act according to the file extension
    if file_path.endswith('.pdf'):
        return read_pdf(file_path)
    elif file_path.endswith('.docx'):
        return read_docx(file_path)
    elif file_path.endswith('.txt'):
        return read_txt(file_path)
    else:
        raise ValueError("Unsupported file format")
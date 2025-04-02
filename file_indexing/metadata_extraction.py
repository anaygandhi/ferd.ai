import os
import time
import fitz 
from docx import Document

# Extracting metadata from a PDF file
def extract_pdf_metadata(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata  
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "file_size": os.path.getsize(pdf_path) 
        }
    except Exception as e:
        return {"error": f"Failed to extract PDF metadata: {e}"}

# Extracting metadata from a DOCX file
def extract_docx_metadata(docx_path):
    try:
        doc = Document(docx_path)
        metadata = doc.core_properties
        return {
            "title": metadata.title,
            "author": metadata.author,
            "subject": metadata.subject,
            "keywords": metadata.keywords,
            "last_modified_by": metadata.last_modified_by,
            "created": metadata.created.isoformat() if metadata.created else "",
            "modified": metadata.modified.isoformat() if metadata.modified else "",
            "file_size": os.path.getsize(docx_path)
        }
    except Exception as e:
        return {"error": f"Failed to extract DOCX metadata: {e}"}

# Extracting metadata from a TXT file
def extract_txt_metadata(txt_path):
    try:
        return {
            "file_name": os.path.basename(txt_path),
            "file_size": os.path.getsize(txt_path),
            "created": time.ctime(os.path.getctime(txt_path)),
            "modified": time.ctime(os.path.getmtime(txt_path))
        }
    except Exception as e:
        return {"error": f"Failed to extract TXT metadata: {e}"}

# Main metadata extraction in any file type 
def extract_metadata(file_path):
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    file_extension = file_path.lower().split('.')[-1]

    if file_extension == "pdf":
        return extract_pdf_metadata(file_path)
    elif file_extension == "docx":
        return extract_docx_metadata(file_path)
    elif file_extension == "txt":
        return extract_txt_metadata(file_path)
    else:
        return {"error": "Unsupported file type"}
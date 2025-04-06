import os
import time
import pymupdf 
from docx import Document


def extract_pdf_metadata(pdf_path:str) -> dict[str, str|int]:
    """Extracts the metadata from the given PDF file."""
    try:
        doc = pymupdf.open(pdf_path)
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


def extract_docx_metadata(docx_path:str) -> dict[str, str|int]:
    """Extracts the metadata from the given docx file."""

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



def extract_txt_metadata(txt_path:str) -> dict[str, str|int]:
    """Extracts the metadata from the given txt file."""

    try:
        return {
            "file_name": os.path.basename(txt_path),
            "file_size": os.path.getsize(txt_path),
            "created": time.ctime(os.path.getctime(txt_path)),
            "modified": time.ctime(os.path.getmtime(txt_path))
        }
    except Exception as e:
        return {"error": f"Failed to extract TXT metadata: {e}"}


def extract_metadata(file_path:str) -> dict[str, str|int]:
    """Extracts the metadata from the given file."""

    # Make sure file exists
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    # Get the file extension
    file_extension:str = file_path.lower().split('.')[-1]

    # Call the appropriate function for this extension
    match file_extension:
        case 'pdf': 
            return extract_pdf_metadata(file_path)
        case 'docx': 
            return extract_docx_metadata(file_path)
        case 'txt': 
            return extract_txt_metadata(file_path)
        case _: 
            return {"error": "Unsupported file type"}
        

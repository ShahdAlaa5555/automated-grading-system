import fitz  # PyMuPDF

def extract_text(pdf_path):
    """
    Reads a PDF file and returns all its text.
    """
    document = fitz.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text

//////// digital pdf
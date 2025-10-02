import fitz  # PyMuPDF(other name) extract pdf text , uses less ram ,alternates->pdfplumber(good for tables,slower),pdfminer(complex but heavy)
import docx

def extract_text_from_pdf(file_path):
    text = ""
    pdf = fitz.open(file_path)
    for page in pdf:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

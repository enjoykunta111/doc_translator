import fitz  # PyMuPDF
from docx import Document
import os

SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt']

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    pages = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        text = "\n".join([b[4].strip() for b in blocks if b[4].strip()])
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        pages.append({
            "page_number": page_num,
            "paragraphs": paragraphs
        })
        #첫 페이지만 반환
        break
    return pages

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    return paragraphs

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)  # 페이지별 구조 반환
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        with open(file_path, encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")

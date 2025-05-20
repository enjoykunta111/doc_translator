import re

def split_paragraph_to_sentences(paragraph):
    # 마침표, 느낌표, 물음표 뒤에서 문장 분리
    sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
    # 빈 문장/공백 제거
    return [s for s in sentences if s.strip()]

from .ollama_translate import translate_with_ollama

def build_structure(text):
    # PDF(페이지별 구조) 처리
    if isinstance(text, list) and len(text) > 0 and isinstance(text[0], dict) and 'page_number' in text[0]:
        result = []
        for page in text:
            page_number = page["page_number"]
            page_paragraphs = []
            for i, para in enumerate(page["paragraphs"]):
                sentences = split_paragraph_to_sentences(para)
                page_paragraphs.append({
                    "paragraph_index": i,
                    "sentences": [
                        {"original": s, "translated": translate_with_ollama(s, model='exaone3.5:2.4b')} for s in sentences
                    ]
                })
            result.append({
                "page_number": page_number,
                "paragraphs": page_paragraphs
            })
        return result
    # 기존 방식 (문단 리스트 또는 문자열)
    if isinstance(text, list):
        paragraphs = [p for p in text if p.strip()]
    else:
        paragraphs = [p for p in text.split('\n') if p.strip()]
    structure = []
    for i, para in enumerate(paragraphs):
        sentences = split_paragraph_to_sentences(para)
        structure.append({
            "paragraph_index": i,
            "sentences": [
                {"original": s, "translated": translate_with_ollama(s, model='exaone3.5:2.4b')} for s in sentences
            ]
        })
    return structure

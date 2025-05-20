from docling.document_converter import DocumentConverter
import fitz  # PyMuPDF
import os

def extract_partial_pdf(src_pdf_path, dst_pdf_path, start_page=0, end_page=2):
    # start_page, end_page는 0-indexed, end_page 포함
    src_doc = fitz.open(src_pdf_path)
    dst_doc = fitz.open()
    for page_num in range(start_page, end_page + 1):
        dst_doc.insert_pdf(src_doc, from_page=page_num, to_page=page_num)
    dst_doc.save(dst_pdf_path)
    dst_doc.close()
    src_doc.close()

import requests
import json
import yaml

def call_ollama_llm(prompt, model='exaone3.5:2.4b'):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
            stream=True
        )
        print(f"[Ollama 응답코드] {response.status_code}")
        lines = response.iter_lines(decode_unicode=True)
        result = ""
        for line in lines:
            print(f"[Ollama 응답라인] {line}")
            try:
                data = json.loads(line)
                if "response" in data:
                    result += data["response"]
            except Exception as e:
                print("[Ollama 응답 파싱 오류]", e)
        print(f"[Ollama 최종 파싱 결과] {result.strip()}")
        return result.strip()
    except Exception as e:
        print(f"Ollama 응답 오류: {e}")
        return ""

def load_restore_markdown_prompt(markdown_text):
    """
    restore_markdown_prompt.yaml에서 description, template을 읽어 실제 프롬프트 문자열을 생성
    """
    yaml_path = os.path.abspath("../prompt/restore_markdown_prompt.yaml")
    with open(yaml_path, 'r', encoding='utf-8') as f:
        prompts = yaml.safe_load(f)
    desc = prompts['restore_markdown']['description'].strip()
    template = prompts['restore_markdown']['template'].replace('{{markdown_text}}', markdown_text)
    return desc + "\n\n" + template

def test_docling_partial_pdf_to_markdown():
    full_pdf_path = os.path.abspath("../data/chapter02.pdf")
    partial_pdf_path = "chapter02_partial.pdf"
    # 예: 1~3페이지(0,1,2)만 추출
    extract_partial_pdf(full_pdf_path, partial_pdf_path, start_page=0, end_page=2)

    converter = DocumentConverter()
    result = converter.convert(partial_pdf_path)
    markdown = result.document.export_to_markdown()
    with open("chapter02_partial_docling.md", "w", encoding="utf-8") as f:
        f.write(markdown)
    print("1~3페이지만 변환된 마크다운 결과가 chapter02_partial_docling.md 파일로 저장되었습니다.")

    # ------ LLM(ollama exaone3.5:2.4b)로 마크다운 구조 복원 ------
    prompt = load_restore_markdown_prompt(markdown)
    print("[Ollama] 마크다운 구조 복원 요청 중...")
    fixed_markdown = call_ollama_llm(prompt, model="exaone3.5:2.4b")
    with open("chapter02_partial_docling_revised.md", "w", encoding="utf-8") as f:
        f.write(fixed_markdown)
    print("LLM으로 복원된 결과가 chapter02_partial_docling_revised.md 파일로 저장되었습니다.")

if __name__ == "__main__":
    test_docling_partial_pdf_to_markdown()
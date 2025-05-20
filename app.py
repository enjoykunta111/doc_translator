import os
from flask import Flask, jsonify, request, Response, stream_with_context, render_template
import os
from tkinter import Tk, filedialog
import json
from document_parser.parser import extract_text
from document_parser.structure_builder import split_paragraph_to_sentences, build_structure
from document_parser.ollama_translate import translate_with_ollama

app = Flask(__name__)

SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt']
SELECTED_FOLDER = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_folder')
def select_folder():
    global SELECTED_FOLDER
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory()
    SELECTED_FOLDER = folder
    if not folder:
        return jsonify([])
    def find_files_in_folder(folder_path, recursive=True):
        file_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    file_list.append(os.path.relpath(os.path.join(root, file), folder_path))
            if not recursive:
                break
        return file_list

    files = find_files_in_folder(folder)
    return jsonify(files)

@app.route('/translate_file')
def translate_file():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'filename 파라미터가 필요합니다.'}), 400
    filepath = os.path.join(SELECTED_FOLDER, filename)
    try:
        text = extract_text(filepath)
        structure = build_structure(text)
        return jsonify(structure)
    except Exception as e:
        import traceback
        print("파일 파싱 중 오류 발생:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# SSE 방식 번역 스트리밍
@app.route('/stream_translate_file')
def stream_translate_file():
    def error_stream(msg):
        yield f"data: {{\"error\": \"{msg}\"}}\n\n"
    filename = request.args.get('filename')
    if not filename:
        return Response(stream_with_context(error_stream("filename 파라미터가 필요합니다.")), content_type='text/event-stream')
    filepath = os.path.join(SELECTED_FOLDER, filename)
    def event_stream():
        try:
            text = extract_text(filepath)
            # PDF 구조만 우선 처리
            if isinstance(text, list) and len(text) > 0 and isinstance(text[0], dict) and 'page_number' in text[0]:
                for page in text:
                    page_number = page['page_number']
                    for i, para in enumerate(page['paragraphs']):
                        sentences = split_paragraph_to_sentences(para)
                        for j, s in enumerate(sentences):
                            print(f"[번역 요청] page={page_number}, paragraph={i}, sentence={j}\n원문: {s}")
                            translated = translate_with_ollama(s, model='exaone3.5:2.4b')
                            print(f"[번역 결과] {translated}\n")
                            data = {
                                'page_number': page_number,
                                'paragraph_index': i,
                                'sentence_index': j,
                                'original': s,
                                'translated': translated
                            }
                            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            else:
                # 기존 방식(문단 리스트)
                if isinstance(text, list):
                    paragraphs = [p for p in text if p.strip()]
                else:
                    paragraphs = [p for p in text.split('\n') if p.strip()]
                for i, para in enumerate(paragraphs):
                    sentences = split_paragraph_to_sentences(para)
                    for j, s in enumerate(sentences):
                        print(f"[번역 요청] paragraph={i}, sentence={j}\n원문: {s}")
                        translated = translate_with_ollama(s, model='exaone3.5:2.4b')
                        print(f"[번역 결과] {translated}\n")
                        data = {
                            'paragraph_index': i,
                            'sentence_index': j,
                            'original': s,
                            'translated': translated
                        }
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except Exception as e:
            import traceback
            print("SSE 번역 중 오류 발생:", e)
            traceback.print_exc()
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    return Response(stream_with_context(event_stream()), content_type='text/event-stream')

import requests
import json
import yaml
import os

def load_prompt(template_key, **kwargs):
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompt', 'tax_translation_prompt.yaml')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompts = yaml.safe_load(f)
    template = prompts[template_key]['template']
    return template.replace('{{source_sentence}}', kwargs.get('source_sentence', '')).replace('{{source_paragraph}}', kwargs.get('source_paragraph', ''))

def translate_with_ollama(text, model='exaone3.5:2.4b'):
    # 문장 단위 번역 프롬프트 사용
    prompt = load_prompt('sentence_translation', source_sentence=text)
    print("[Ollama 호출 준비] 모델:", model)
    print("[Ollama 프롬프트]", prompt)
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
        print(f"[Ollama 최종 번역 결과] {result.strip()}")
        return result.strip()
    except Exception as e:
        print(f"Ollama 번역 오류: {e}")
        return ""
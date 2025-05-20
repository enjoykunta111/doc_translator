import webview
import threading
import time
import requests
from app import app

def start_flask():
    app.run(debug=False, port=5000, use_reloader=False)

def wait_for_server(url, timeout=10):
    for _ in range(timeout * 10):
        try:
            requests.get(url)
            return True
        except:
            time.sleep(0.1)
    return False

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()

    print("🌐 Flask 서버 준비 중...")
    if wait_for_server("http://localhost:5000"):
        print("✅ Flask 서버 시작됨. 웹뷰 창 띄우는 중...")
        webview.create_window("문서 번역기", "http://localhost:5000")
        webview.start()
    else:
        print("❌ Flask 서버가 시작되지 않았습니다.")

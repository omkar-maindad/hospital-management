import webview
from app import app
import threading

def start_server():
    # Boot the Flask server silently on a background thread
    print("CareSync Desktop Engine Starting...")
    app.run(port=5001, use_reloader=False)

if __name__ == '__main__':
    # 1. Start the actual website
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 2. Boot the Native Windows Desktop window wrapped around the site
    print("Launching Native Windows GUI...")
    webview.create_window('CareSync Hospital System', 'http://127.0.0.1:5001', width=1280, height=800)
    webview.start()

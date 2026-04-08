import webview
import sys
import os
import threading
from dotenv import load_dotenv

# When bundled, PyInstaller stores assets in a temporary MEIPASS folder
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# CRITICAL FIX: Force load the exact packaged .env file BEFORE app imports database.py
env_path = os.path.join(base_path, '.env')
load_dotenv(env_path)

# Inject the paths into the Flask app before running
from app import app
app.template_folder = os.path.join(base_path, 'templates')
app.static_folder = os.path.join(base_path, 'static')

def start_server():
    # Run the Flask Local server silently on background port
    app.run(port=5001, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Use physical ICO for taskbar and window
    icon_path = os.path.join(base_path, 'static', 'icons', 'icon.ico')
    
    # Launch Native Application
    webview.create_window(
        'CareSync Hospital System', 
        'http://127.0.0.1:5001', 
        width=1280, 
        height=800
    )
    webview.start(icon=icon_path)

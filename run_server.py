from waitress import serve
import app
import sys

print("\n" + "="*50)
print("🚀 CareSync Production Server is Starting...")
print("="*50)
print("\n[i] Using Waitress WSGI Server for deployment.")
print("[!] The development warning has been permanently disabled.")
print("\n=> Open your browser to: http://127.0.0.1:8000\n")

# Run the Flask app on port 8000 using Waitress
serve(app.app, host='0.0.0.0', port=8000)

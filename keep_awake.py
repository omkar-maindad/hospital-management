import time
import urllib.request
import datetime
import sys

url = "https://caresync-hpms.onrender.com"
interval = 9 * 60  # Ping every 9 minutes

print("==================================================")
print("     CARESYNC RENDER ANTI-SLEEP ENGINE ACTIVE     ")
print("==================================================")
print(f"Target URL: {url}")
print("Leave this window open in the background.")
print("It prevents Render from putting your Mobile App to sleep!")
print("==================================================\n")

while True:
    try:
        response = urllib.request.urlopen(url)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sent invisible pulse! Server awake.")
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Pulse error (Check internet): {e}")
    time.sleep(interval)

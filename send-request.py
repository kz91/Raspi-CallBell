from datetime import datetime
import sys
import requests

PICO_W_IPS = sys.argv[1:]
PICO_W_PORT = 80
responses = []

for PICO_W_IP in PICO_W_IPS:
    response = requests.post(f"http://{PICO_W_IP}:{PICO_W_PORT}")
    print("Call: ", PICO_W_IP)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    responses.append(f"[{current_time}] {response.text}")

for resp in responses:
    print(resp)

import sys
import requests

PICO_W_IPS = sys.argv[1:]
PICO_W_PORT = 80
responses = []

for PICO_W_IP in PICO_W_IPS:
    response = requests.post(f"http://{PICO_W_IP}:{PICO_W_PORT}")
    print("call: ", PICO_W_IP)
    responses.append(response.text)

for resp in responses:
    print(resp)

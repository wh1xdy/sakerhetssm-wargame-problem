import requests
import base64
import json
import random
import os
import time

BASE_URL = "http://flask:5000"
IMAGE_DIR = "images"                 # folder with random images

def visit_homepage():
    try:
        r = requests.get(f"{BASE_URL}/")
        print("[+] Visited homepage:", r.status_code)
    except Exception as e:
        print("[-] Failed to visit homepage:", e)

def get_token():
    try:
        r = requests.get(f"{BASE_URL}/token")
        token = r.json().get("token")
        print("[+] Got token:", token)
        return token
    except Exception as e:
        print("[-] Failed to get token:", e)
        return None

def pick_random_image():
    files = [f for f in os.listdir(IMAGE_DIR) if not f.startswith(".")]

    if not files:
        raise Exception("No images found in folder!")

    chosen = random.choice(files)
    path = os.path.join(IMAGE_DIR, chosen)
    print(f"[+] Using random image: {chosen}")
    return path

def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

def send_evaluate(token, image_b64):
    payload = {
        "auth": {
            "user": "user",
            "token": token
        },
        "image": image_b64
    }

    try:
        r = requests.post(f"{BASE_URL}/evaluate", json=payload)
        print("[+] Evaluate response:", r.json())
    except Exception as e:
        print("[-] Evaluate request failed:", e)

def loop_traffic():
    print("[*] Starting traffic simulator...")
    while True:
        print("\n=== New Traffic Event ===")

        visit_homepage()
        token = get_token()

        if token:
            img_path = pick_random_image()
            encoded = encode_image(img_path)
            send_evaluate(token, encoded)

        delay = random.randint(30, 50)
        print(f"[+] Waiting {delay} seconds before next event...\n")
        time.sleep(delay)

if __name__ == "__main__":
    time.sleep(10)
    loop_traffic()

import requests
import base64
import random
import os
import jwt
import time
import datetime

BASE_URL = "http://flask:5000"

SECRET_KEY = "p4lt_4_l1fe_0r_wh4t_d0_y0u_s4y?"

def get_token():
    payload = {
        "user": "admin",
        "role": "admin",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token

def visit_homepage():
    try:
        r = requests.get(f"{BASE_URL}/")
        print("[+] Visited homepage:", r.status_code)
    except Exception as e:
        print("[-] Failed to visit homepage:", e)

def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

def send_evaluate(token, image_b64):
    payload = {
        "auth": {
            "user": "admin",      # change to "admin" if you need admin behavior
            "token": token
        },
        "image": image_b64
    }

    try:
        r = requests.post(f"{BASE_URL}/evaluate", json=payload)
        print("[+] Evaluate response:", r.json())
    except Exception as e:
        print("[-] Evaluate request failed:", e)

if __name__ == "__main__":
    time.sleep(300)
    visit_homepage()
    token = get_token()

    if token:
        encoded = encode_image("./palt.png")
        send_evaluate(token, encoded)

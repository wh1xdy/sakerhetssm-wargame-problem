import smtplib
from email.message import EmailMessage

import requests
import base64
import json
import random
import os
import time

BASE_URL = "http://flask:5000"
SMTP_HOST = "smtp"
SMTP_PORT = 1025

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

def send_mail_with_image():
    msg = EmailMessage()
    msg["Subject"] = "Help urgently needed!!"
    msg["From"] = "grandma@xebccxnxrobyntrgno.com"
    msg["To"] = "customer-support@paltoverflow.com"
    msg.set_content("Hello,\n\nI've desperatly tried my best to upload this image to the PaltReviewer, but it doesn't work. Could you maybe try it, I urgently need the score.")

    # Read the image
    with open("palt.png", "rb") as f:
        img_data = f.read()

    # Add the image attachment
    msg.add_attachment(
        img_data,
        maintype="image",
        subtype="png",
        filename="palt.png"
    )

    # Send it
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.send_message(msg)

if __name__ == "__main__":
    time.sleep(100)

    visit_homepage()
    token = get_token()

    if token:
        img_path = "./palt.png"
        encoded = encode_image(img_path)
        send_evaluate(token, encoded)

    time.sleep(10)

    visit_homepage()
    token = get_token()

    if token:
        img_path = "./palt.png"
        encoded = encode_image(img_path)
        send_evaluate(token, encoded)

    time.sleep(100)

    send_mail_with_image()

#!/usr/bin/env python3

import sys
import hashlib

import requests
from Crypto.Util.number import isPrime
from PIL import Image
from pyzbar import pyzbar

secret = []
url_from_qr_code = pyzbar.decode(Image.open("fra-qr-screenshot.png"))[0].data.decode()
print(f"URL: {url_from_qr_code}")

for i in range(len(url_from_qr_code)):
    if isPrime(i):
        secret.append(url_from_qr_code.encode()[i])
secret = bytes(secret)

key_material = "This is the way.".encode()
key_raw = bytes(x ^ y for x, y in zip(key_material, secret))
key = hashlib.md5(key_raw).hexdigest()

url2 = f"{url_from_qr_code}/{key}"
print(f"URL 2: {url2}")

r = requests.get(url2)
sys.stdout.buffer.write(r.content)

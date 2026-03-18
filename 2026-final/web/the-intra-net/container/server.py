import os
import io
import random
import string
import time

from flask import Flask, render_template, request, Response, abort
from PIL import Image, ImageDraw, ImageFont
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

app = Flask(__name__)

captcha_images = {}
token_images = {}

FLAG = os.environ.get("FLAG", "SSM{mock}")

_key_rng = random.Random(int(time.time()))
CAPTCHA_SECRET = bytes([_key_rng.randint(0, 255) for _ in range(16)])


def encrypt_answer(answer):
    padder = padding.PKCS7(128).padder()
    padded = padder.update(answer.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(CAPTCHA_SECRET), modes.ECB())
    enc = cipher.encryptor()
    return (enc.update(padded) + enc.finalize()).hex()


def decrypt_answer(hex_ct):
    ct = bytes.fromhex(hex_ct)
    cipher = Cipher(algorithms.AES(CAPTCHA_SECRET), modes.ECB())
    dec = cipher.decryptor()
    padded = dec.update(ct) + dec.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode()


def generate_captcha():
    answer = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # --- captcha image (distorted text) ---
    img = Image.new("RGB", (240, 80), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36
        )
    except OSError:
        font = ImageFont.load_default()

    for _ in range(300):
        x, y = random.randint(0, 239), random.randint(0, 79)
        c = tuple(random.randint(160, 220) for _ in range(3))
        draw.point((x, y), fill=c)

    for _ in range(6):
        coords = [
            (random.randint(0, 239), random.randint(0, 79)),
            (random.randint(0, 239), random.randint(0, 79)),
        ]
        draw.line(coords, fill=(180, 180, 200), width=1)

    x_pos = 20
    for ch in answer:
        y_off = random.randint(-5, 5)
        draw.text((x_pos, 18 + y_off), ch, font=font, fill=(40, 40, 80))
        x_pos += 34

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    captcha_png = buf.getvalue()

    # --- token image (encrypted answer as pixel data) ---
    ct_hex = encrypt_answer(answer)
    ct_bytes = bytes.fromhex(ct_hex)

    scale = 12
    margin = 4
    width = len(ct_bytes) * scale + margin * 2
    height = scale + margin * 2

    token_img = Image.new("RGB", (width, height), color=(245, 240, 250))
    token_draw = ImageDraw.Draw(token_img)

    for i, b in enumerate(ct_bytes):
        x0 = margin + i * scale
        y0 = margin
        r = b
        g = (b * 73 + 53) % 256
        bl = (b * 137 + 97) % 256
        token_draw.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill=(r, g, bl))

    buf = io.BytesIO()
    token_img.save(buf, format="PNG")
    token_png = buf.getvalue()

    captcha_images[ct_hex] = captcha_png
    token_images[ct_hex] = token_png

    return ct_hex


@app.route("/")
def index():
    ct_hex = generate_captcha()
    return render_template("index.html", captcha_token=ct_hex)


@app.route("/captcha/<token>")
def captcha_image(token):
    data = captcha_images.get(token)
    if data is None:
        abort(404)
    return Response(data, mimetype="image/png")


@app.route("/token/<token>")
def token_image(token):
    data = token_images.get(token)
    if data is None:
        abort(404)
    return Response(data, mimetype="image/png")


@app.route("/request", methods=["GET", "POST"])
def request_fence():
    params = request.form if request.method == "POST" else request.args
    captcha_answer = params.get("captcha", "").strip().upper()
    token = params.get("captcha_token", "")
    name = params.get("name", "").strip()

    try:
        correct_answer = decrypt_answer(token)
    except Exception:
        return render_template(
            "result.html",
            success=False,
            message="Invalid CAPTCHA token. Please reload the page and try again.",
        )

    if not name:
        return render_template(
            "result.html",
            success=False,
            message="You must enter your name.",
        )

    if captcha_answer == correct_answer:
        return render_template(
            "result.html",
            success=True,
            message=f"Thank you {name}! Your fence order has been registered.",
            flag=FLAG,
        )
    else:
        return render_template(
            "result.html",
            success=False,
            message="Wrong CAPTCHA answer. Please try again.",
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)

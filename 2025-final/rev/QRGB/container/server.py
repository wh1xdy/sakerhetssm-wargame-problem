from flask import *

import os
import cv2
import hashlib
import qrcode
import numpy as np
import math
import re


app = Flask(__name__)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/generate_qr", methods=["POST"])
def generate_qr():
    data = json.loads(request.data.decode("utf-8")).get("data")
    hash = hashlib.md5(data.encode()).hexdigest()
    path = f"codes/qr{hash}.png"
    if not os.path.exists(path):
        cv2.imwrite(path, encode(data))

    return url_for("codes", code=f"qr{hash}.png")


@app.route("/codes/<code>", defaults={"size": -1}, methods=["GET"])
@app.route("/codes/<code>/<size>", methods=["GET"])
def codes(code, size):
    # Prevents path traversal
    if re.match(r"^[a-zA-Z0-9_-]+$", code) is not None:
        return "Invalid code", 400
    # Ensures that the image size is in bounds 0-1000
    if cast_to_int(size, 0, 1000) == -1:
        return send_file(f"codes/{code}")
    size = int(size)
    img = cv2.imread(f"codes/{code}")
    resized = cv2.resize(
        img,
        (
            int(img.shape[1] * int(size) / 100),
            int(img.shape[0] * int(size) / 100),
        ),
        interpolation=cv2.INTER_NEAREST,
    )
    cv2.imwrite(f"codes/resized_{code}", resized)
    return send_file(f"codes/resized_{code}")


def calc_rgb(data):
    sizes = [len(data) // 3 + (i < len(data) % 3) for i in range(3)]
    rl, gl, bl = (
        data[: sizes[0]],
        data[sizes[0] : sizes[0] + sizes[1]],
        data[sizes[0] + sizes[1] :],
    )
    r = sum((1 << (7 - i)) for i, b in enumerate(rl) if not b)
    g = sum((1 << (7 - i)) for i, b in enumerate(gl) if not b)
    b = sum((1 << (7 - i)) for i, b in enumerate(bl) if not b)
    return (b, g, r)  # idk why this is reversed but it works


def encode(data, box_size=1):
    seg_length = max(math.ceil(len(data) / 24), 25)

    segments = [data[i : i + seg_length] for i in range(0, len(data), seg_length)][:24]
    matrixes = []
    qr = qrcode.QRCode(error_correction=1, box_size=1, border=0)
    qr.add_data(segments[0])
    for seg in segments:
        qr.data_list.clear()
        qr.add_data(seg)
        matrixes.append(qr.get_matrix())

    qr_size = len(matrixes[0])
    img = np.zeros((qr_size, qr_size, 3), dtype=np.uint8)
    for y in range(qr_size):
        for x in range(qr_size):
            img[y, x] = calc_rgb([m[y][x] for m in matrixes])

    resized = cv2.resize(
        img,
        (qr_size * box_size, qr_size * box_size),
        interpolation=cv2.INTER_NEAREST,
    )
    return resized


def cast_to_int(value, min, max):
    try:
        return int(value) if int(value) >= min and int(value) <= max else -1
    except ValueError:
        return -1


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

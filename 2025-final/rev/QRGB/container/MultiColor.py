import qrcode
import numpy as np
import cv2
import math


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

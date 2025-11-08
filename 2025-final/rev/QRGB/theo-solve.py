import cv2
from pyzbar.pyzbar import decode
import numpy as np
import bases


def solve(filename):
    print("Solving", filename)
    multi_color = cv2.imread(filename)
    shape = multi_color.shape

    # Initialize a numpy array for codes
    codes = np.zeros((24, shape[0], shape[1]), dtype=bool)

    for y in range(shape[0]):
        for x in range(shape[1]):
            r, g, b = multi_color[y, x]
            for i in range(8):
                codes[i, y, x] = bool((r >> i) & 1)
                codes[i + 8, y, x] = bool((g >> i) & 1)
                codes[i + 16, y, x] = bool((b >> i) & 1)

    data = b""

    for i, code in enumerate(codes[::-1]):
        if np.sum(code) == 0:
            continue
        bool_matrix = code.astype(np.uint8)
        bw_image = bool_matrix * 255

        resized = cv2.resize(
            bw_image,
            (len(bw_image) * 3, len(bw_image) * 3),
            interpolation=cv2.INTER_NEAREST,
        )
        decoded = decode(resized)
        data += decoded[0].data

    if "{" in data.decode():
        return data.decode()
    else:
        with open("tmp.png", "wb") as f:
            f.write(bases.base45.decode(data.decode()))
        return solve("tmp.png")


print(solve("flag.png"))

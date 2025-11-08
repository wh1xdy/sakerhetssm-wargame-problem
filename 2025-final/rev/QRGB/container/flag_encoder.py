import MultiColor
import cv2
import bases

flag = "SSM{53cur17y_7hr0u6h_hu35cur17y}"
filename = "flag.png"


def obfuscate(data, iterations=1):
    for _ in range(iterations):
        cv2.imwrite(filename, MultiColor.encode(data))
        data = bases.base45.encode(open(filename, "rb").read())


obfuscate(flag, 10)
print("Done")

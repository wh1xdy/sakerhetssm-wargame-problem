#!/usr/bin/env python3

import os, io

from PIL import Image # pip -> pillow
import pyzbar.pyzbar # pip -> pyzbar
import base45 # pip -> base45

# result_HEJ.png -> b'HEJ' rgb = 0, bit = 7

# result_småSTORAsiffror.png ->
# b'abcdefghijklmnopqrstuvwxy' rgb = 0, bit = 7
# b'z\xe7\x96\x87\xe7\x93\xa3\xe7\xb9\xb9ABCDEFGHIJKLMNOPQRSTU' rgb = 1, bit = 7
# b'VWXYZ\xc3\x85\xc3\x84\xc3\x960123456789' rgb = 2, bit = 7

# python3 -c "print(*[x for x in range(12000)], sep='_')" > 0-11999.png

def decodeImage(im):
    # im = Image.open(os.path.join(os.path.dirname(__file__), '0-11999.png'))
    # im = Image.open(path)
    pix = im.load()
    print(im.size)

    totalData = b''

    for rgb in range(3):
        for bit in range(7, -1, -1):
            foreground = Image.new('RGBA', (im.size[0], im.size[1]), (255, 255, 255, 255))
            fim = foreground.load()
            for x in range(im.size[0]):
                # print(f'{x = :0>3} {tuple(map(lambda n: f"{n:0>8b}", pix[x,0])) = }')
                for y in range(im.size[1]):
                    # print(pix[x,y])
                    colorValue = pix[x,y][rgb]
                    if not colorValue & (1 << bit):
                        fim[x,y] = (0,0,0)
                    else:
                        fim[x,y] = (255,255,255)


            background = Image.new('RGBA', (im.size[0] + 10, im.size[1] + 10), (255, 255, 255, 255))
            background.paste(foreground, (5, 5))

            decoded = pyzbar.pyzbar.decode(background)
            if len(decoded) != 1:
                print(f'Decoded length: {len(decoded) = }, {rgb = }, {bit = }')
            else:
                data = decoded[0].data
                print(data[:100], f'{rgb = }, {bit = }')
                totalData += data

            # background.save(os.path.join(os.path.dirname(__file__), 'test', f'{"RGB"[rgb]}-{bit}.png'))

    decoded = totalData.decode()

    if len(decoded) < 100:
        print(decoded)
    else:
        print(f'{decoded[:50]} ... {decoded[-50:]}')

    return totalData

data = decodeImage(Image.open(os.path.join(os.path.dirname(__file__), 'flag.png')))

while True:
    b45decoded = base45.b45decode(data)
    print(f'{b45decoded[:100] = }')

    data = decodeImage(Image.open(io.BytesIO(b45decoded)))

    if data.startswith(b'SSM{'):
        print(f'FLAG: {data}')
        break
    else:
        print(data[:100])

# exit()

# with open(os.path.join(os.path.dirname(__file__), 'out.bin'), 'wb') as outfile:
#     outfile.write(data)

# byteCount = {}

# for byte in data:
#     if byte not in byteCount:
#         print(f'{chr(byte)} ({byte:x}) not previously seen')
#         byteCount[byte] = 0
#     byteCount[byte] += 1

# for byte in sorted(byteCount):
#     print(f'{chr(byte)} ({byte:x}) found {byteCount[byte]} times')
# print(f'Total length: {len(byteCount)}')

import json

import math


"""

d: lilla visaren
b: stora visaren
c: position, y
a: position, x

"""

import re
import json

# Input data (you can also read this from a file)
data = """
    <use xlink:href="#clock" style="--b: 21938; --c: 2376357; --d: -233; --a: -395820" />
    <use xlink:href="#clock" style="--c: 2376236; --a: -395735; --b: 20134; --d: -246" />
    <use xlink:href="#clock" style="--d: -201; --c: 2376237; --b: 19718; --a: -395735" />
    <use xlink:href="#clock" style="--c: 2376285; --d: -161; --b: 20134; --a: -395856" />
    <use xlink:href="#clock" style="--b: 19718; --a: -395855; --c: 2376236; --d: -201" />
    <use xlink:href="#clock" style="--c: 2376357; --a: -395735; --d: -233; --b: 20134" />
    <use xlink:href="#clock" style="--c: 2376357; --b: 19459; --d: -201; --a: -395756" />
    <use xlink:href="#clock" style="--b: 19459; --d: -233; --a: -395735; --c: 2376245" />
    <use xlink:href="#clock" style="--c: 2376236; --d: -182; --b: 19234; --a: -395756" />
    <use xlink:href="#clock" style="--b: 20134; --a: -395856; --d: -246; --c: 2376357" />
    <use xlink:href="#clock" style="--b: 19718; --d: -233; --a: -395831; --c: 2376357" />
    <use xlink:href="#clock" style="--b: 20134; --d: -201; --a: -395840; --c: 2376236" />
    <use xlink:href="#clock" style="--b: 19234; --d: -201; --c: 2376261; --a: -395735" />
    <use xlink:href="#clock" style="--d: -201; --b: 21938; --a: -395735; --c: 2376285" />
    <use xlink:href="#clock" style="--c: 2376357; --d: -182; --a: -395792; --b: 19234" />
    <use xlink:href="#clock" style="--a: -395855; --b: 19718; --c: 2376357; --d: -246" />
    <use xlink:href="#clock" style="--b: 20678; --d: -201; --a: -395807; --c: 2376357" />
    <use xlink:href="#clock" style="--d: -201; --c: 2376336; --b: 20134; --a: -395856" />
    <use xlink:href="#clock" style="--b: 19298; --d: -246; --a: -395735; --c: 2376240" />
    <use xlink:href="#clock" style="--c: 2376236; --b: 19459; --a: -395852; --d: -233" />
    <use xlink:href="#clock" style="--c: 2376236; --a: -395792; --b: 19234; --d: -233" />
    <use xlink:href="#clock" style="--a: -395735; --d: -281; --c: 2376336; --b: 19459" />
    <use xlink:href="#clock" style="--d: -233; --a: -395856; --c: 2376300; --b: 20134" />
    <use xlink:href="#clock" style="--b: 19234; --a: -395840; --d: -233; --c: 2376357" />
    <use xlink:href="#clock" style="--d: -182; --b: 19234; --a: -395856; --c: 2376252" />
    <use xlink:href="#clock" style="--c: 2376317; --b: 19298; --d: -246; --a: -395735" />
    <use xlink:href="#clock" style="--d: -233; --c: 2376236; --b: 20134; --a: -395820" />
    <use xlink:href="#clock" style="--a: -395735; --c: 2376272; --d: -201; --b: 20678" />
    <use xlink:href="#clock" style="--a: -395856; --c: 2376317; --d: -201; --b: 19459" />
    <use xlink:href="#clock" style="--d: -233; --b: 19718; --c: 2376357; --a: -395852" />
    <use xlink:href="#clock" style="--d: -246; --a: -395856; --b: 19298; --c: 2376261" />
    <use xlink:href="#clock" style="--d: -161; --a: -395807; --c: 2376236; --b: 20134" />
    <use xlink:href="#clock" style="--d: -138; --b: 20134; --a: -395775; --c: 2376357" />
    <use xlink:href="#clock" style="--a: -395847; --c: 2376236; --b: 20134; --d: -246" />
    <use xlink:href="#clock" style="--c: 2376357; --a: -395847; --d: -233; --b: 21938" />
    <use xlink:href="#clock" style="--d: -201; --a: -395856; --b: 19718; --c: 2376236" />
    <use xlink:href="#clock" style="--d: -233; --a: -395735; --c: 2376252; --b: 20134" />
    <use xlink:href="#clock" style="--a: -395735; --b: 19459; --c: 2376300; --d: -201" />
    <use xlink:href="#clock" style="--b: 19298; --c: 2376236; --d: -246; --a: -395775" />
    <use xlink:href="#clock" style="--c: 2376236; --d: -201; --a: -395831; --b: 19459" />
    <use xlink:href="#clock" style="--c: 2376272; --b: 19234; --d: -233; --a: -395856" />
""".strip()

# Regular expression to capture a, b, c, d values from style
pattern = re.compile(r'--a:\s*([-\d]+).*?--b:\s*([-\d]+).*?--c:\s*([-\d]+).*?--d:\s*([-\d]+)', re.DOTALL)
reverse_pattern = re.compile(r'--b:\s*([-\d]+).*?--c:\s*([-\d]+).*?--d:\s*([-\d]+).*?--a:\s*([-\d]+)', re.DOTALL)

# Collect parsed rows
rows = []
for line in data.splitlines():
    # Normalize order by capturing regardless of order
    matches = dict(re.findall(r'--([abcd]):\s*([-\d]+)', line))
    if all(k in matches for k in ('a', 'b', 'c', 'd')):
        rows.append({
            'a': int(matches['a']),
            'b': int(matches['b']),
            'c': int(matches['c']),
            'd': int(matches['d'])
        })

# thanks chatgpt ^ https://chatgpt.com/share/690fd2de-b04c-8005-9494-f289e49aa747

def decode(item):
    a = item["a"]
    b = item["b"]
    c = item["c"]
    d = item["d"]

    x = 292800 * (a + 395856) ** 0.5 / 2928
    y = 27200 * (c - 2376236) ** 0.5 / 272


    d = (d + 282) ** 0.5 / 864 * 25920
    b = (b - 19234) ** 0.5 / 160320 * 961920

    d = int(d) % 360
    b = int(b) % 360


    # dumb rounding 
    d = d if d != 132 else 135
    b = b if b != 132 else 135

    d = d if d != 48 else 45
    b = b if b != 48 else 45

    d = d if d != 210 else 225
    b = b if b != 210 else 225

    d = d if d != 228 else 225
    b = b if b != 228 else 225

    d = d if d != 312 else 315
    b = b if b != 312 else 315

    d = d if d != 30 else 45
    b = b if b != 30 else 45

    d = d if d != 300 else 315
    b = b if b != 300 else 315

    d = d if d != 330 else 315
    b = b if b != 330 else 315

    
    return (x, y, d, b)

data2 = [decode(item) for item in rows]

max_x = max(data2, key=lambda x: x[0])[0]
min_x = min(data2, key=lambda x: x[0])[0]

max_y = max(data2, key=lambda x: x[1])[1]
min_y = min(data2, key=lambda x: x[1])[1]

# print(max_x, max_y, min_x, min_y) # 1100.0 1100.0 0.0 0.0

middle = (max_x + min_x) / 2, (max_y + min_y) / 2


def get_angle(item):
    base = item[0] - middle[0]
    perp = item[1] - middle[1]

    return math.atan2(perp, base)

data2.sort(key=get_angle)

# https://chatgpt.com/share/690fcc0b-36dc-8005-ae25-01819cd4aa03
# chatgpt sucks at angles, had to fix it manually, could be partially wrong
angles_to_letter = {
    (180, 225): "A",
    (180, 270): "B",
    (180, 315): "C",
    (180, 0): "D",
    (180, 45): "E",
    (180, 90): "F",
    (180, 135): "G",
    (225, 270): "H",
    (225, 315): "I",
    (0, 90): "J",
    (225, 0): "K",
    (225, 45): "L",
    (225, 90): "M",
    (225, 135): "N",
    (270, 315): "O",
    (270, 0): "P",
    (270, 45): "Q",
    (270, 90): "R",
    (270, 135): "S",
    (315, 0): "T",
    (315, 45): "U",
    (315, 135): "V",
    (45, 90): "W",
    (45, 135): "X",
    (315, 90): "Y",
    (90, 135): "Z",
    (180, 180): " "
}


def decode_flag(left_angle, right_angle):
    return angles_to_letter.get((left_angle, right_angle), angles_to_letter.get((right_angle, left_angle), "?"))

flag = ''.join([decode_flag(int(item[2]), int(item[3])) for item in data2])
flag = ''.join([flag[2:], flag[:2]])

print(flag.replace("BRACKET", "{", 1).replace("BRACKET", "}").replace(" ", ""))


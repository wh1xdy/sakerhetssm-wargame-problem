import random
import numpy as np
from PIL import Image
from pathlib import Path

out_dir = Path('./site')
flag = b'SSM{https://media.tenor.com/hzFHhdvD3lAAAAAM/gato-joia.gif#}'

assert len(flag)%4==0, f'{len(flag)%4=}'
nchunks = len(flag)//4
chunks = [flag[i:i+4] for i in range(0, len(flag), 4)]

ok = np.array(Image.open('ok.png').convert('1')).astype(np.uint8)

imh, imw = ok.shape
bg = np.random.randint(0, 2, size=(imh, imw*nchunks), dtype=np.uint8)

Image.fromarray(bg * 255).save(out_dir/'bg.png')

for i in range(nchunks):
    Image.fromarray((bg[:, i*imw:(i+1)*imw] ^ ok) * 255).save(out_dir/f'm{i}.png')

def random_rot():
    angle = np.random.uniform(-np.pi, np.pi)
    return (
        f'rotate({angle}rad)',
        np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
    )

def random_scale():
    sx, sy = np.random.uniform(0.1, 1.5, size=2)
    return (
        f'scale({sx}, {sy})',
        np.array([
            [sx, 0],
            [0, sy]
        ])
    )

def random_skew():
    ax, ay = np.random.uniform(-np.pi/4, np.pi/4, size=2)
    return (
        f'skew({ax}rad, {ay}rad)',
        np.array([
            [1, np.tan(ax)],
            [np.tan(ay), 1]
        ])
    )

def random_transform():
    return random.choice([random_rot, random_scale, random_skew])()

org_mats = [np.array(list(chunk)).reshape(2, 2) for chunk in chunks]
transform_lists = []

prefix_len = 10
for org_mat in org_mats:
    transforms = []

    tot = np.eye(2)
    for _ in range(prefix_len):
        s, mat = random_transform()
        transforms.append(s)
        tot @= mat

    last = np.linalg.inv(org_mat) @ np.linalg.inv(tot)
    transforms.insert(0, f'matrix({last[0,0]}, {last[1,0]}, {last[0,1]}, {last[1,1]}, 0, 0)')

    transform_lists.append(transforms)

with open('chall_template.html', 'r') as f:
    template = f.read()

mat_s = ''
for i, transforms in enumerate(transform_lists):
    transforms.insert(0,
        f'matrix(var(--m{i}00), var(--m{i}10), var(--m{i}01), var(--m{i}11), 0, 0)'
    )
    transforms.append(f'translateX({i*imw}px)')
    mat_s += f'<img src="./m{i}.png" style="mix-blend-mode:difference;'\
             f'position:absolute;pointer-events: none;left:0px;top:0px;'\
             f'image-rendering: pixelated;transform:{" ".join(transforms)};">\n'

template = template.replace('NUM_CHUNKS', str(nchunks))
template = template.replace('IMGS_HERE', mat_s)
with open(out_dir/'index.html', 'w') as f:
    f.write(template)
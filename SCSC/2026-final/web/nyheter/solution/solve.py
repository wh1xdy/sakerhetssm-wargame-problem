import requests
from time import sleep
import sys

NEWS_HOST = '127.0.0.1:3000'



for x in range(1,20):
    try:
        res = requests.get(f'http://{NEWS_HOST}/api/search?q=SCSC')
        assert res.json()['count'] == 1
        break
    except:
        sleep(1)
res = requests.get(f'http://{NEWS_HOST}/api/search?q=SCSX')
assert res.json()['count'] == 0

flag = 'SCSC{1_Am_t3H_AnsV@riG_uTG1vare_n0W}'
res = requests.get(f'http://{NEWS_HOST}/api/search?q={flag}')
assert res.json()['count'] == 1
res = requests.get(f'http://{NEWS_HOST}/api/search?q=x{flag}x')
assert res.json()['count'] == 0

print(flag)
import requests as r
import re

REGEX = r'flag">(.*)<'
BASE_URL = 'http://127.0.0.1:50000'

resp = r.get(BASE_URL, allow_redirects=False)

matches = re.search(REGEX, resp.text)
first = matches.group(1)

resp = r.get(BASE_URL + '/second.php')
matches = re.search(REGEX, resp.text)
second = matches.group(1)

print(first + second)
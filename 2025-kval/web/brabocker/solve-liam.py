import requests
import re

url = "http://localhost:50000"

res = requests.get(url + "/comment?id=2")

print(re.search(r"SSM\{.*?\}", res.text).group(0))

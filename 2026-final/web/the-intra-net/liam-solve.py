import requests
import base64

URL = "http://127.0.0.1:50000/track"


def get_chunk(url, start, end):
    data = {"url": url, "start": start, "end": end}
    response = requests.post(URL, data=data)
    res = response.text
    idx1 = res.find('; font-size: 13px;">') + len('; font-size: 13px;">')
    idx2 = res.find("</pre>", idx1)
    enc = res[idx1:idx2]
    return bytes.fromhex(base64.b64decode(enc).decode())


def get_all(url):
    start = 0
    chunk_size = 50
    result = bytearray()

    while True:
        chunk = get_chunk(url, start, start + chunk_size)
        if not chunk:
            break
        result.extend(chunk)
        start += chunk_size

    return bytes(result)


tok = get_chunk("http://127.0.0.1:8080/", 6833, 6833 + 50)
token = tok.split(b'"')[0].decode()

cap = get_all("http://127.0.0.1:8080/captcha/" + token)
with open("captcha.png", "wb") as f:
    f.write(cap)

answer = input("input answer: ")

res = get_all(
    f"http://127.0.0.1:8080/request?captcha_token={token}&captcha={answer}&name=Tester"
)
print(res)

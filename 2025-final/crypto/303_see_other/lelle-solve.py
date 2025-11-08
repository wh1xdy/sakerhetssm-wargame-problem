import randcrack
import requests as s

r = s.Session()

url = "http://127.0.0.1:50000"

samples = []
for _ in range(624 // 4):
    sample = r.get(url + "/robots.txt").content.split(b"/")[1]
    for i in range(4):
        to_add = sample[8*(3-i) : 8*(3-i) + 8]
        samples.append(int(to_add.decode(), 16))


cracker = randcrack.RandCrack()
for sample in samples:
    cracker.submit(sample)

print(r.get(url + "/" + hex(cracker.predict_getrandbits(128))[2:]).content)

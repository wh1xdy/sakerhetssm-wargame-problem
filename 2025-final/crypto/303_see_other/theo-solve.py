import requests
from randcrack import RandCrack

url = "<URL>"  # eg. http://127.0.0.1:50000

cookie = requests.get(url).cookies["user_hash"]

rc = RandCrack()  # https://github.com/tna0y/Python-random-module-cracker

# Randcrack needs 624 32 bit integers to recreate the random state.
# The server provides a 128 bit number which we can split into 4 32 bit integers.
for i in range(624 // 4):
    response = requests.get(url + "/robots.txt", cookies={"user_hash": cookie})
    last_flag = response.text.split("/")[1]
    for fragment in [last_flag[i : i + 8] for i in range(0, len(last_flag), 8)][::-1]:
        rc.submit(int(fragment, 16))


# The generated flag is built from 4 32 bit integers in big endian notation.
next_flag = "".join(
    [rc.predict_getrandbits(32).to_bytes(4, "big").hex() for _ in range(4)][::-1]
)

print(requests.get(f"{url}/{next_flag}", cookies={"user_hash": cookie}).text)

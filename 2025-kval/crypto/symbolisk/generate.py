#!/usr/bin/env python
import string

plain_alph = string.ascii_lowercase + " \n"
enc_alph = """🙀
🚹
🙎
🚿
🚇
🛱
🚩
😸
😜
🛋
🚫
🚰
🚬
🛀
😡
😕
🚔
🙅
😔
🙊
😭
😑
🙄
🚚
😮
😚
😎""".split("\n")
enc_alph.append("\n")

assert len(plain_alph) == len(enc_alph)

lookup = {k:v for k, v in zip(plain_alph, enc_alph)}

with open("---KVALIFICERAT_HEMLIG---.txt", "w") as f:
    f.write(f"""
=====================

{"\n".join(enc_alph)}
=====================
""")

with open("Meddelande #452.txt", "w") as f:
    f.write("".join([lookup[c] for c in "the flag is signsofhiddenmeanings"]) + "\n")


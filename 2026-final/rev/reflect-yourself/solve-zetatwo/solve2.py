#!/usr/bin/env python3

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

"""
string.Join("\n", System.IO.Directory.GetFiles("."))
# ./ReflectYourself.dll

System.Convert.ToBase64String(System.IO.File.ReadAllBytes("./ReflectYourself.dll"))
# TVqQA...

echo TVqQA..." | base64 -d > ReflectYourself.dll
dnSpy -> analyze
"""

key = [101, 98, 205, 40, 155, 212, 65, 77, 154, 144, 215, 34, 17, 176, 68, 68, 157, 39, 192, 237, 238, 172, 221, 74, 243, 170, 9, 181, 61, 109, 213, 156]
ciphertext = [117, 33, 182, 152, 158, 0, 183, 15, 23, 137, 174, 10, 111, 12, 14, 148, 17, 68, 117, 120, 254, 142, 240, 175, 115, 169, 223, 198, 66, 198, 85, 211, 205, 43, 190, 55, 59, 100, 133, 157, 224, 221, 187, 150, 161, 222, 169, 173]

aes = AES.new(key=bytes(key), mode=AES.MODE_ECB)
plaintext = aes.decrypt(bytes(ciphertext))
plaintext = unpad(plaintext, block_size=16)
print(plaintext.decode())

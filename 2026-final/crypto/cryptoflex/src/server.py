#!/usr/bin/env python3

import os

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from typing import Tuple, Optional


BITS = 2048
FLAG = os.environ.get("FLAG", "SSM{placeholder_flag}")


class Logger:
    def __init__(self):
        self.debug = False

    def log(self, message):
        if self.debug:
            print(f"[?] {message}")


log = Logger()


def gcd(a: int, b: int) -> Tuple[int, int]:
    if a == 0 or b == 0:
        return 1, 1
    r = a % b
    d = 1
    while r:
        d += 1
        a = b
        b = r
        r = a % b
    return d, b


def encrypt(key: RSA, message: bytes) -> bytes:
    log.log("Encrypting with RSA-PKCS1-OAP")
    cipher = PKCS1_OAEP.new(key)
    return cipher.encrypt(message)


def decrypt(key: RSA, message: bytes) -> bytes:
    log.log("Decrypting with RSA-PKCS1-OAP")
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(message)


def menu():
    print("1. Set exponent")
    print("2. Encrypt message")
    print("3. Get encrypted flag")
    print("4. Exit")
    return int(input("Choice: ").strip())


def set_exponent(key: RSA, e: int) -> Optional[RSA]:
    log.log("Calculating RSA components")
    phi = (key.p - 1) * (key.q - 1)
    i, g = gcd(e, phi)
    log.log(f"Calculated GCD(e, phi) in {i} iterations")
    if g != 1:
        print("Bad e, gcd(e, phi) != 1")
        return None

    log.log("Constructing RSA key")
    try:
        d = pow(e, -1, phi)
        new_key = RSA.construct((key.n, e, d, key.p, key.q), consistency_check=False)
    except Exception:
        log.debug = True
        log.log("Error constructing RSA key, enabling debug mode to help troubleshoot")
        return None

    log.log("Testing RSA key")
    m1 = "THIS_IS_A_TEST_MESSAGE".encode()
    log.log("Encrypting test message")
    c1 = encrypt(new_key, m1)
    log.log("Decrypting test ciphertext")
    m2 = decrypt(new_key, c1)
    log.log("Validating decryption")
    if m1 != m2:
        print("Encryption test failed")
        return None

    return key


def encrypt_message(key: RSA) -> None:
    message = input("Please enter a message: ").strip()
    c = encrypt(key, message.encode())
    print("Encrypted message:")
    print(c.hex())


def main():
    print('Welcome to CryptoFlex 3000!')
    print('Generating key...')
    key = RSA.generate(BITS, e=0x10001)
    print('Key created')
    print(f'N: {key.n}')
    print(f'e: {key.e}')
    encrypted_flag = encrypt(key, FLAG.encode())

    while True:
        choice = menu()
        match choice:
            case 1:
                new_e = int(input("Please enter new exponent: ").strip())
                newkey = set_exponent(key, new_e)

                if newkey:
                    key = newkey
                    print("Updated exponent")
                else:
                    print("Failed to update exponent")
            case 2:
                encrypt_message(key)
            case 3:
                print(f"Here is the flag: {encrypted_flag.hex()}")
            case 4:
                print("Goodbye!")
                break
            case _:
                print("Invalid option")


if __name__ == "__main__":
    main()

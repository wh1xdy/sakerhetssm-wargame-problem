#!/usr/bin/env python3

import struct
import sys

FLAG = b"SCSC{tistel_is_a_feistel_verifier}"
ROUNDS = 8


def rol32(x, r):
    r &= 31
    return ((x << r) | (x >> (32 - r))) & 0xFFFFFFFF


def ror32(x, r):
    r &= 31
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF


def load_le32(b):
    return struct.unpack("<I", b)[0]


def store_le32(x):
    return struct.pack("<I", x & 0xFFFFFFFF)


MASTER_KEY = [
    0xC0FFEE11,
    0x0BADC0DE,
    0x8BADF00D,
    0xFEEDFACE,
]

ROUND_CONSTS = [
    0xA5F1523D,
    0x1B037387,
    0x3C6EF372,
    0xBB67AE85,
    0x6A09E667,
    0x510E527F,
    0x9B05688C,
    0x1F83D9AB,
]


def subkey(i):
    k = MASTER_KEY[i & 3]
    k ^= rol32(MASTER_KEY[(i + 1) & 3], 5 + i)
    k = (k + (0x9E3779B9 * (i + 1))) & 0xFFFFFFFF
    return k


def round_f(r, k, c):
    x = (r + k) & 0xFFFFFFFF
    x ^= rol32(r, 7 + (c & 7))
    x = (x + (c ^ ror32(k, 11 + (c & 3)))) & 0xFFFFFFFF
    x ^= rol32(x, 13)
    return x


def enc_block(block8):
    l = load_le32(block8[:4])
    r = load_le32(block8[4:])
    for i in range(ROUNDS):
        k = subkey(i)
        f = round_f(r, k, ROUND_CONSTS[i])
        l, r = r, (l ^ f) & 0xFFFFFFFF
    # output swap: (R_{n+1}, L_{n+1})
    return store_le32(r) + store_le32(l)


def pkcs7_pad(data, block=8):
    pad = block - (len(data) % block)
    if pad == 0:
        pad = block
    return data + bytes([pad]) * pad


def c_array_u8(name, b):
    hexes = ", ".join(f"0x{x:02x}" for x in b)
    return f"static const uint8_t {name}[{len(b)}] = {{ {hexes} }};\n"


def c_array_u32(name, arr):
    hexes = ", ".join(f"0x{x:08x}u" for x in arr)
    return f"static const uint32_t {name}[{len(arr)}] = {{ {hexes} }};\n"


def main():
    padded = pkcs7_pad(FLAG, 8)
    out = bytearray()
    for off in range(0, len(padded), 8):
        out += enc_block(padded[off : off + 8])

    sys.stdout.write("#pragma once\n")
    sys.stdout.write("#include <stdint.h>\n\n")
    sys.stdout.write(f"#define FLAG_LEN {len(FLAG)}u\n")
    sys.stdout.write(f"#define TARGET_LEN {len(out)}u\n\n")
    sys.stdout.write(c_array_u32("MASTER_KEY", MASTER_KEY))
    sys.stdout.write("\n")
    sys.stdout.write(c_array_u32("ROUND_CONSTS", ROUND_CONSTS))
    sys.stdout.write("\n")
    sys.stdout.write(c_array_u8("TARGET", bytes(out)))


if __name__ == "__main__":
    main()

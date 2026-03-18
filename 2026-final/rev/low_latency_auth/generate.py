import struct
import os

ARRAY_SIZE = 100000
PASSWORD = b"HolyGuacamoles!?"

def mixer(password: bytes) -> list[int]:
    state = list(struct.unpack(">8H", password))
    for round_num in range(16):
        for i in range(8):
            state[i] = (state[i] + state[(i - 1) % 8]) & 0xFFFF
            state[i] ^= (0x9E37 + round_num) & 0xFFFF
            state[i] = ((state[i] << 7) | (state[i] >> 9)) & 0xFFFF
    return state

def hash_chunk(chunk: int, pos: int) -> int:
    h = chunk ^ ((pos * 0x5bd1e995) & 0xFFFFFFFFFFFFFFFF)
    h ^= (h >> 15)
    h = (h * 0xbf58476d1ce4e5b9) & 0xFFFFFFFFFFFFFFFF
    h = ((h * h) ^ (h >> 32)) & 0xFFFFFFFFFFFFFFFF
    h = (h * 0x94d049bb133111eb) & 0xFFFFFFFFFFFFFFFF
    h ^= (h >> 31)
    return h

def main():
    filter_array = [int.from_bytes(os.urandom(8), 'big') for _ in range(ARRAY_SIZE)]
    chunks = mixer(PASSWORD)
    expected_fp = 0
    filter_sum = 0
    indices = []

    for i in range(8):
        h = hash_chunk(chunks[i], i)
        idx = (h & 0xFFFFFFFF) % ARRAY_SIZE
        fp = h

        indices.append(idx)
        expected_fp ^= fp
        if i < 7:
            filter_sum ^= filter_array[idx]

    filter_array[indices[7]] = expected_fp ^ filter_sum

    with open("xor_filter.h", "w") as f:
        f.write(f"// Auto-generated xor-filter\n")
        f.write(f"#include <stdint.h>\n\n")
        f.write(f"const uint64_t FILTER_ARRAY[{ARRAY_SIZE}] = {{\n")
        for i in range(0, ARRAY_SIZE, 4):
            row = ", ".join([f"0x{val:016X}ULL" for val in filter_array[i:i+4]])
            f.write(f"    {row},\n")
        f.write("};\n")


if __name__ == "__main__":
    main()

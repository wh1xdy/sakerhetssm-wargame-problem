import struct
import re
from collections import defaultdict
from pwn import remote

ARRAY_SIZE = 100000
MASK64 = 0xFFFFFFFFFFFFFFFF

def load_array_from_header(filename="xor_filter.h"):
    filter_array = []
    with open(filename, "r") as f:
        content = f.read()

    matches = re.findall(r"0x([0-9A-Fa-f]+)ULL", content)
    for match in matches:
        filter_array.append(int(match, 16))

    assert len(filter_array) == ARRAY_SIZE
    return filter_array

def hash_chunk(chunk: int, pos: int) -> int:
    h = chunk ^ ((pos * 0x5bd1e995) & MASK64)
    h ^= (h >> 15)
    h = (h * 0xbf58476d1ce4e5b9) & MASK64
    h = ((h * h) & MASK64) ^ (h >> 32)
    h = (h * 0x94d049bb133111eb) & MASK64
    h ^= (h >> 31)
    return h

def inverse_mixer(target_chunks: list[int]) -> bytes:
    state = list(target_chunks)

    for round_num in range(15, -1, -1):
        for i in range(7, -1, -1):
            state[i] = ((state[i] >> 7) | (state[i] << 9)) & 0xFFFF
            state[i] ^= (0x9E37 + round_num) & 0xFFFF
            state[i] = (state[i] - state[(i - 1 + 8) % 8]) & 0xFFFF

    return struct.pack(">8H", *state)


def merge_lists(left_list, right_list, next_shift: int):
    merged = defaultdict(list)
    for prefix in left_list:
        if prefix not in right_list:
            continue

        for chunksL, vL in left_list[prefix]:
            for chunksR, vR in right_list[prefix]:
                xor_val = vL ^ vR
                merged[xor_val >> next_shift].append((chunksL + chunksR, xor_val))

    return merged


def solve():
    FILTER_ARRAY = load_array_from_header()

    print("[*] Phase 1: Hashing")
    lists = [defaultdict(list) for _ in range(8)]

    for pos in range(8):
        for chunk_val in range(65536):
            h = hash_chunk(chunk_val, pos)
            idx = (h & 0xFFFFFFFF) % ARRAY_SIZE
            fp = h

            wagner_val = FILTER_ARRAY[idx] ^ fp

            prefix = wagner_val >> 48
            lists[pos][prefix].append((chunk_val, wagner_val))

    print("[*] Phase 2: Layer 1 merge")
    L1 = [defaultdict(list) for _ in range(4)]
    base_pair_positions = [(0, 1), (2, 3), (4, 5), (6, 7)]

    for i in range(4):
        left_list = lists[i*2]
        right_list = lists[i*2 + 1]

        for prefix in left_list:
            if prefix in right_list:
                for cL, vL in left_list[prefix]:
                    for cR, vR in right_list[prefix]:
                        xor_val = vL ^ vR
                        next_prefix = xor_val >> 32
                        L1[i][next_prefix].append(([cL, cR], xor_val))

    print("[*] Phase 3: Layer 2 merge")
    second_layer_pairings = [
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    ]

    for pairing_idx, pairing in enumerate(second_layer_pairings, start=1):
        L2 = [
            merge_lists(L1[pairing[0][0]], L1[pairing[0][1]], 0),
            merge_lists(L1[pairing[1][0]], L1[pairing[1][1]], 0),
        ]

        print("[*] Phase 4: Layer 3 merge")
        left_final, right_final = L2

        for xor_val, left_items in left_final.items():
            if xor_val not in right_final:
                continue

            right_items = right_final[xor_val]
            final_chunks = left_items[0][0] + right_items[0][0]

            pair_order = [
                pairing[0][0],
                pairing[0][1],
                pairing[1][0],
                pairing[1][1],
            ]
            position_order = [
                pos for pair_idx in pair_order for pos in base_pair_positions[pair_idx]
            ]
            ordered_chunks = [0] * 8
            for pos, chunk in zip(position_order, final_chunks):
                ordered_chunks[pos] = chunk

            forged_password = inverse_mixer(ordered_chunks)
            print(f"[+] solution found: {forged_password.hex()}")
            io = remote('localhost', 50000)
            io.recvuntil(b'> ')
            io.sendline(forged_password.hex().encode())
            print(io.recv().decode())
            return

    print("[-] :(")

if __name__ == "__main__":
    solve()

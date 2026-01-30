from os import urandom

def random_below(n):
    byte_count = (n.bit_length() + 7) // 8
    random_bytes = urandom(byte_count)
    random_number = int.from_bytes(random_bytes) % n
    
    return random_number

def shift_bits(array):
    output = []

    for i in range(len(array)):
        if random_below(192) > 95:
            output.append(1 - array[i])
        else:
            output.append(array[i])
    
    return output

with open("flag.txt") as f:
    flag = int.from_bytes(f.read().encode())
    flag_array = [int(x) for x in bin(flag)[2:]]
    while len(flag_array) % 8 != 0:
        flag_array = [0] + flag_array
    
with open("output.txt", "w") as f:
    for _ in range(128):
        flips = shift_bits(flag_array)
        f.write("".join(map(str, flips)) + "\n")
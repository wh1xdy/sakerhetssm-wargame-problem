from sys import exit

# enum OP {
#     OP_CPY = 0x0,
#     OP_DEL = 0x1,
#     OP_XOR = 0x2,
#     OP_NOR = 0x3,
#     OP_AND = 0x4,
#     OP_ROT = 0x5,
# };

data = b""


def copy(idx, d):
    global data
    if len(d) != 8:
        print("Wrong len")
        exit(-1)

    data += bytes([0x0, idx])
    data += d


def delete(idx):
    global data
    data += bytes([0x1, idx])


def xor(c, a, b):
    global data
    data += bytes([0x2, c, a, b])


def nor(c, a, b):
    global data
    data += bytes([0x3, c, a, b])


def and_(c, a, b):
    global data
    data += bytes([0x4, c, a, b])


def rot(b, a, amount):
    global data
    data += bytes([0x5, b, a, amount])


def not_(c, a):
    nor(c, a, a)


def or_(c, a, b):
    nor(c, a, b)
    not_(c, c)


def emit():
    hex_str = data.hex()
    print(f"{len(data)}")
    print(hex_str)

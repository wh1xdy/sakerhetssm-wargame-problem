from sage.all import GF, Zmod, matrix, vector, ideal, block_matrix
from Crypto.Util.number import bytes_to_long

ring = GF(2)[",".join(f"x{i}" for i in range(0, 256))]
xs = ring.gens()
print(xs)

Zn = Zmod(2**32)

outs = []
with open("out.txt") as f:
    for line in f.readlines():
        wine = bytearray(map(lambda x: int(x, 16), line.split()))
        outs.append(wine)

################################################


def rotl(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & 0xFFFFFFFFFFFFFFFF


def next_rand(s) -> int:
    r1 = s[1] * 5
    r1 &= 0xFFFFFFFF
    r2 = (r1 ^ (r1 << 7)) * 9
    r2 &= 0xFFFFFFFF
    t = s[1] << 17
    s[2] ^= s[0]
    s[3] ^= s[1]
    s[1] ^= s[2]
    s[0] ^= s[3]
    s[2] ^= t
    s[3] = rotl(s[3], 45)

    for i in range(4):
        s[i] &= 0xFFFFFFFFFFFFFFFF

    return r2


def vec_to_sta(vec):
    s = [0, 0, 0, 0]
    for i, c in enumerate(vec):
        ir = i % 64
        iq = i // 64

        s[iq] |= c << (63 - ir)

    return s


def sta_to_vec(sta):
    vec = [0] * 256
    for i, c in enumerate(sta):
        for ii in range(64):
            vec[i*64 + ii] = int(((c >> (63 - ii)) & 1) != 0)

    return vec


M = matrix.diagonal([1] * 256)
B = []
for row in M:
    state = vec_to_sta(row)
    next_rand(state)
    B.append(sta_to_vec(state))
B = matrix(GF(2), B)
M = matrix(GF(2), M)

rand_mat = B.T * M.inverse()
print(type(rand_mat))
print(type(rand_mat ** 10))
print("made random marrix")

############################################################

dots = [
    2276344508, 3868698040, 2932233957, 2481846377, 3315139130, 1079154857,
    546696388,  2042452297, 2280531969, 3382719674, 1837261007, 352190692,
    547788629,  2406082427, 1197860883, 376254976,  3001847785, 2516055065,
    2848289332, 471417044,  120242309,  3247271329, 2552421204, 2399516480,
    3128873567, 3305266045, 976269268,  2353587310, 3818595075, 557748429,
    209807908,  459673187
][::-1]


def prep_knacksack():
    seen = {}
    for i in range(2**16):
        sum = 0
        ii = i
        while ii != 0:
            idx = (ii & -ii).bit_length() - 1
            ii = ii & (ii-1)
            sum += dots[idx]

        seen[sum % 2**32] = i

    def solve_knap(tot):
        solves = []
        for i in range(2**16):
            i <<= 16
            sum = 0
            ii = i
            while ii != 0:
                idx = (ii & -ii).bit_length() - 1
                ii = ii & (ii-1)
                sum += dots[idx]

            if (tot - sum) % 2**32 in seen:
                solve = int(i) | int(seen[(tot - sum) % 2**32])
                solves.append(solve)

        # print(list(map(hex, solves)))
        return solves
    return solve_knap


knapper = prep_knacksack()


def mask(inp):
    sum = 0
    for i in range(32):
        bit = (inp >> i) & 1
        sum += bit * dots[i]

    return sum


###########################################################
# leaking flag format outputs & decoding


formats = 11


def leak_outs():
    solved = []
    counts = []
    i = -1
    while len(solved) != formats:
        i += 1
        val = (outs[i][0] << 24) | (outs[i][1] << 16) | (
            outs[i][2] << 8) | (outs[i][3])
        val ^= bytes_to_long(b"SSM{")
        solve = knapper(val)
        if len(solve) > 1:
            continue

        solved.append(solve[0])
        counts.append(i)
        print(f"knapsacked {i+1} out of {formats}")

    return solved, counts


def vec_int(xs): return sum([int(x) << i for i, x in enumerate(xs)])
def int_vec_32(x): return vector([(x >> i) & 1 for i in range(32)][::-1])
def vec_int_256(xs): return sum([int(x) << i for i, x in enumerate(xs)])
def int_vec_256(x): return vector([(x >> i) & 1 for i in range(256)][::-1])
def dot(es): return sum([xs[i] * es[i] for i in range(32)])


def invert_rand(a):
    def invert_shift(x):
        result = 0
        for i in range(0, 32, 7):
            x_bits = (x >> i) & ((1 << 7) - 1)
            if i >= 7:
                prev_bits = (result >> (i-7)) & ((1 << 7) - 1)
            else:
                prev_bits = 0
            current_bits = x_bits ^ prev_bits
            result |= (current_bits << i)
        return result
    a9 = pow(9, -1, 2**32) * a % 2**32
    a7 = invert_shift(a9)
    a5 = pow(5, -1, 2**32) * a7 % 2**32

    return a5


#########################

num1 = 0x3333333333333333FFFFFFFFFFFFFFFF
num1v = int_vec_256(num1)
num1s = vec_to_sta(num1v)

num2s = num1s[:]
next_rand(num2s)
num2v = sta_to_vec(num2s)

num3v = matrix(GF(2), rand_mat) * vector(GF(2), num1v)

assert vector(GF(2), num2v) == vector(GF(2), num3v)  # rand_mat is correct

##########################

solved, counts = leak_outs()
starters = list(map(invert_rand, solved))
print(f"{list(map(hex, starters))=}")  # matches :)
print(f"{counts=}")
matrices = [rand_mat**(10*i)
            for i in counts]  # mul 10 to make counts correct
www = matrices[0][96:128]
print(www.ncols(), www.nrows())


def flatten(xss): return [
    x
    for xs in xss
    for x in xs
]


s = list(map(int_vec_32, starters))
chonker = block_matrix(GF(2), [[matrices[i][96: 128]]
                       for i in range(len(matrices))])
print(f"{(chonker.nrows(), chonker.ncols())=}")
assert chonker.nrows() == 352
assert chonker.ncols() == 256
longer = vector(GF(2), flatten(s))
init = chonker.solve_right(longer)
assert len(init) > 0

init_vec = [int(a) for a in init]
print(init_vec)
init_state = vec_to_sta(init_vec)


flag = outs[0][:]
print(f"{len(flag)=}")
for i in range(len(outs[0]) // 4):
    rand = mask(next_rand(init_state))
    print(hex(rand))
    for ii in range(4):
        flag[4*i+ii] ^= (rand >> 8*(3-ii)) & 0xFF

print(bytes(flag).decode())

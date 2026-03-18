flag_len = 45

macros = open("macros.h", "r").readlines()
macros = macros[1 + flag_len:-1]
macro_count = len(macros)

def from_db(dbs: list[str]):
    db = dbs[0]
    idx = int(db[2:])
    ret = [None] * (len(dbs)-1)
    counter_dbs = [0] * (len(dbs)-1)
    counter_ends = [0] * flag_len
    for i, db in enumerate(dbs[1:]):
        if db.startswith("db"):
            index = int(db[2:]) - 1
            counter_dbs[index] += 1
        else:
            index = int(db[3:]) - 1
            counter_ends[index] += 1
            

    return (idx, counter_ends, counter_dbs)

state = {}
counter_lookup = {}
ends_lookup = {}

def add_vec(vec1, vec2):
    vec3 = []
    for a, b in zip(vec1, vec2):
        vec3.append(a + b)
    return tuple(vec3)

def mul_vec(vec, mul):
    ret = [a*mul for a in vec]
    return tuple(ret)

def vec_set(vec, idx, elem):
    ret = list(vec)
    ret[idx] = elem
    return tuple(ret)

def is_zero(lsit):
    for i in lsit:
        if i != 0:
            return False
    return True

def recurse(idx, reclim):
    reclim = vec_set(reclim, idx-1, 0)
    ret = tuple([0] * flag_len)
    if (idx, reclim) in state:
        return state[(idx, reclim)]

    origlim = reclim
    for i, c in enumerate(ends_lookup[idx]):
        # print(i, c)
        tmp = tuple([0] * flag_len)
        tmp = vec_set(tmp, i, c)
        ret = add_vec(ret, tmp)
    for (i, c), mul in zip(enumerate(reclim), counter_lookup[idx]):
        # print(i, c, mul)
        if c == 1:
            add = recurse(i+1, reclim)
            tmp = mul_vec(add, mul)
            ret = add_vec(ret, tmp)

    state[(idx, origlim)] = ret
    return ret


for macro in macros:
    parts = macro.strip().replace(";", "").split()
    parts = parts[1:]

    dbs = from_db(parts)
    counter_lookup[dbs[0]] = dbs[2]
    ends_lookup[dbs[0]] = dbs[1]

sol = tuple([0] * flag_len)
for i in range(1, macro_count+1):
    ans = recurse(i, tuple([1] * macro_count))
    sol = add_vec(sol, ans)

# print(f"{ends_lookup = }")
# print(f"{counter_lookup = }")
# print(f"state = {"\n".join(map(lambda x: f"{x[0]} :: {x[1]}", state.items()))}")
# print(f"{sol = }")
print(" ".join(map(str, sol)))
flag = bytearray(b"SSM{really_wish_we_had_recursive_C_macros_:(}")
fuck_flag = bytearray([0] * len(sol))
for i in range(len(sol)):
    fuck_flag[i] = (sol[i] + flag[i]) % 256

print(bytes(fuck_flag))

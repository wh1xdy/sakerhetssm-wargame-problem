lists = []
samples = 128
with open("output.txt") as f:
    for _ in range(samples):
        lists.append(
            [int(x) for x in f.readline().replace("\n", "")]
            )

instances = [0]*len(lists[0])

for i in lists:
    for j in range(len(i)):
        instances[j] += i[j]

flag_array = [0]*len(instances)
for j, i in enumerate(instances):
    if i > samples // 2:
        flag_array[j] = 1

from Crypto.Util import number

flag = number.long_to_bytes(int("".join(map(str, flag_array)), 2))
print(flag.decode())
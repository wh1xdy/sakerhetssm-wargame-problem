#!/usr/bin/env python

db_defs = []

with open('macros.h', 'r') as f:
	for line in f:
		if line.startswith('#define db'):
			t = ([0 for _ in range(16)], [0 for _ in range(45)])
			for s in line.split(' ')[2:]:
				while s[-1] == ';' or s[-1] == '\n':
					s = s[:-1]
				if s[:2] == 'db':
					t[0][int(s[2:]) - 1] += 1
				else:
					t[1][int(s[3:]) - 1] += 1
			db_defs.append(t)

for i in range(len(db_defs)):
	for j in range(16):
		db_defs[i][0][j] &= 0xff
	for j in range(45):
		db_defs[i][1][j] &= 0xff

def cached(f):
	cache = dict()
	def _impl(a, b):
		if (a, b) in cache:
			return cache[(a, b)]
		ret = f(a, b)
		cache[(a, b)] = ret
		return ret
	return _impl

@cached
def dp(i, x):
	a = [j for j in db_defs[i][1]]
	x |= 1 << i

	for j in range(16):
		if (x & (1 << j)) != 0:
			continue
		f = db_defs[i][0][j]
		b = dp(j, x)
		for k in range(45):
			a[k] += f * b[k]

	for j in range(45):
		a[j] &= 0xff

	return a

flag_enc = b"\xf3g\x81\x05%,\xca'\x17+\xa7\xfd\nS\xacT[\x00\x8d\xc1\x96@&\xb8Qu\xcefc\x19Ye\xef\xef-\xbf\xd0\xc8\xc7i'o\xe5Bg"

def main():
	a = [0 for _ in range(45)]
	for i in range(16):
		b = dp(i, 0)
		for j in range(45):
			a[j] += b[j]
	for i in range(45):
		a[i] &= 0xff

	flac_dec = list(flag_enc)
	for i in range(45):
		flac_dec[i] = (flac_dec[i] - a[i]) % 0x100
	print(bytes(flac_dec))

if __name__ == '__main__':
	main()


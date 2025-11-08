msg = bytearray(b'SSM{c0mput3_r3sp0nsibly_k1ds}')
nums = [*msg]
iters = 1000000
print('Encrypting...')
for _ in range(iters):
	for i in range(len(nums)):
		nums[i] = (nums[i]*1337)%(2**32)
		nums[i]^=nums[(i+1)%len(nums)]
print(nums)
minv = pow(1337,-1,2**32)
# Decode
print('Decrypting...')
flag = nums[::]
for _ in range(iters):
	for i in range(len(nums))[::-1]:
		flag[i]^=flag[(i+1)%len(flag)]
		flag[i]=(flag[i]*minv)%(2**32)
print(bytes(flag))
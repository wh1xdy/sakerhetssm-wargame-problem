import numpy as np
import math
import struct
import mp3
import sys

r = mp3.Decoder(open("flag.mp3", "rb")).read()

samples = struct.unpack("<" + "h" * (len(r) // 2), r)

# count pulse lengths
prev = 0
count = 0
pulses = []

for x in samples:
  if abs(x - prev) > 5000:
    pulses.append((prev > 0, count))    
    count = 0
  count += 1
  prev = x

# glitch filter
progress = True

while progress:
  filtered = []
  progress = False

  i = 0

  while i < len(pulses) - 2:
    if pulses[i + 1][1] < 10:
      filtered.append((pulses[i][0], pulses[i][1] + pulses[i + 1][1] + pulses[i + 2][1]))
      i += 3
      progress = True
    else:
      filtered.append(pulses[i])
      i += 1
  
  pulses = filtered

characters = []

time = 0
primes = []
start_time = 0

# find character start time + prime factor start times
for (p,l) in pulses:
  time += l

  if p and (l == 15397 or (l > 8000 and l < 9500)): # find start pulse (output is high for ~9000 samples), special case for first character
    if start_time != 0:
      characters.append((start_time, primes[:-1], time - start_time))
    start_time = time
    primes = []
  
  if l > 16000 and not p: # between each printout output is low for >16000 samples
    primes.append(time - start_time)

characters.append((start_time, primes, time - start_time))

known = [[-1 for _ in p] for (s, p, l) in characters]

def factor(x):
  res = []
  
  for n in range(2, 127):
    while x % n == 0:
      x = x // n
      res.append(n)
  
  return res

# insert known flag characters
known[0] = factor(ord('S'))
known[1] = factor(ord('C'))
known[2] = factor(ord('S'))
known[3] = factor(ord('C'))
known[4] = factor(ord('{'))
known[31] = factor(ord('}'))

# assume shortest interval between factors is a 2 followed by another 2 (atleast one flag character is a multiple of 4)
print2 = min([p[1] - p[0] for (s, p, l) in characters if len(p) > 1])

done = False
iterations = 0

# iteratively perform least squares estimation to find:
# setup time (time from sync pulse to first increment or factor)
# increment time (time to increment factor by one)
# time to print X (where X = the prime factor printed)
while not done:
  a = []
  b = []
  
  iterations += 1

  for (i, (start, prints, length)) in enumerate(characters):
    for (j, p) in enumerate(prints):
      if known[i][j] != -1:
        a.append(p) # start time of printout X = setup time + increments required to reach this number + time to print previous factors
        
        seq = [1, (known[i][j]-2)]+([0]*125)
        
        for x in known[i][:j]:
          seq[x] += 1
        
        b.append(seq)
      else:
        break
    else: # all factors known, use end time to estimate print time for last factor
      if i != 31: # end time of last character is unknown
        a.append(length) # length = setup time + 125 increments + time to print all factors
        
        seq = [1, 125]+([0]*125)
        
        for x in known[i]:
          seq[x] += 1
        
        b.append(seq) 

  (estimate, _, _, _) = np.linalg.lstsq(b, a)
  
  estimate[2] = print2 # plug in our guess for time to print a '2'
  
  for (i, (start, prints, length)) in enumerate(characters):
    time = estimate[0] # setup time
    last = 2 # factor starts at 2
    
    for (j, p) in enumerate(prints):
      if known[i][j] != -1:
        if estimate[known[i][j]] < 1:
          break
        
        time += (known[i][j] - last) * estimate[1] # add time for increments
        time += estimate[known[i][j]] # add time for printing
      else:
        known[i][j] = int(round(last + ((p - time) / estimate[1]))) # knowing what has been printed up to this point, number of increments can be calculated
        break
      
      last = known[i][j]

  done = sum(known, []).count(-1) == 0

flag = bytes([math.prod(k) for k in known])

assert(sum(flag) == 0xB3E)

print(flag)

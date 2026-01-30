import numpy as np
from numpy import sin, pi
from scipy.io import wavfile

freq = 261.625565
chunk_size = 10_000
threshold = 0.03

nudge = 2 # without this, both phases have identical difference

samplerate, data = wavfile.read("c.wav")
middle_c = sin(2 * pi * (np.arange(len(data)) - nudge) / samplerate * freq) / 2

diff = np.abs(data - middle_c)

bits = ""
for i in range(0, len(diff), chunk_size):
	v = np.sum(diff[i:i+chunk_size]) / chunk_size
	if v < threshold:
		bits += "0"
	else:
		bits += "1"

for i in range(0, len(bits), 8):
	print(chr(int(bits[i:i+8], 2)), end="")
print()

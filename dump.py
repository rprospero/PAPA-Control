import numpy as np
import matplotlib.pyplot as plt

bytes = np.fromfile("..\\1672\\0001.pel",np.uint64,count=50000)[32:]

A = bytes & 0x3FF
B = (bytes>>10) & 0x3FF
C = (bytes>>20) & 0x3FF
D = (bytes >> 30) & 0x3FF

plt.plot(D,'black')
plt.plot(A,'g')
plt.plot(B,'r')
plt.plot(C,'b')
plt.show()


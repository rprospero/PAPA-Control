import numpy as np
import matplotlib.pyplot as plt
import reader
import sys

file = "c:\\Documents and Settings\\sesaadmin\\My Documents\\Neutron Data\\%s\\0001.pel"%sys.argv[1]
p = reader.PelFile(file)
print p.header.AcquisitionMode
bytes = np.fromfile(file,np.uint64,count=200000)[32:]

A = bytes & 0x3FF
B = (bytes>>10) & 0x3FF
C = (bytes>>20) & 0x3FF
D = (bytes >> 30) & 0x3FF

A = A[:128*(len(A)//128)]
B = B[:128*(len(B)//128)]
C = C[:128*(len(C)//128)]
D = D[:128*(len(D)//128)]

A = np.mean(np.reshape(A,(-1,128)),axis=0)
B = np.mean(np.reshape(B,(-1,128)),axis=0)
C = np.mean(np.reshape(C,(-1,128)),axis=0)
D = np.mean(np.reshape(D,(-1,128)),axis=0)

print np.max(A)/np.max(D)
print np.max(B)/np.max(D)
print np.max(C)/np.max(D)
print np.max(D)

plt.plot(A,'g')
plt.plot(B,'r')
plt.plot(C,'b')
plt.plot(D,'black')
plt.show()

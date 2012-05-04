import numpy as np
import matplotlib.pyplot as plt
import reader
import sys

file = "c:\\Documents and Settings\\sesaadmin\\My Documents\\Neutron Data\\%s\\0001.pel"%sys.argv[1]
p = reader.PelFile(file)
print p.header.AcquisitionMode
bytes = np.fromfile(file,np.uint64,count=50000)[32:]

A = bytes & 0x3FF
B = (bytes>>10) & 0x3FF
C = (bytes>>20) & 0x3FF
D = (bytes >> 30) & 0x3FF

#plt.plot(A,'g')
#plt.plot(B,'r')
#plt.plot(C,'b')
#plt.plot(D,'black')
#plt.show()

data = np.transpose(np.asarray(np.vstack((A,B,C,D)),np.uint16))

print data[0:10]

with open("AM%i.txt"%p.header.AcquisitionMode,"w") as outfile:
    outfile.write("ADC A\tADC B\tADC C\tADC D\n")
    np.savetxt(outfile,data,fmt="%i",delimiter="\t")

import reader
import numpy as np
import matplotlib.pyplot as plt
import sys

location = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/%04i/0001.pel"

legend = [['Energy','x9','y9','Strobe'],
          ['x8','x7','y7','Strobe'],
          ['y8','x6','y6','Strobe'],
          ['x5','x4','y4','Strobe'],
          ['y5','x3','y3','Strobe'],
          ['x2','x1','y1','Strobe'],
          ['y2','x0','y0','Strobe'],
          ['ADC A','ADC B','ADC C','ADC D'],
          ['Energy','x9','y9','Strobe']]

def extract(run):
    f = location%run
    p = reader.PelFile(f)
    bytes = np.fromfile(f,np.uint64)[32:]
    A = bytes & 0x3FF
    B = (bytes>>10) & 0x3FF
    C = (bytes>>20) & 0x3FF
    D = (bytes >> 30) & 0x3FF

    return (p.header._asdict(),A,B,C,D)

if __name__=="__main__":
    h,A,B,C,D = extract(int(sys.argv[1]))

    sums = np.zeros((4,128),np.uint32)
    events = np.asarray([0,0,0,0])

    count = len(A)/128 #this is an int
    rem = len(A) % 128
    print count
    A = A[:-rem]
    B = B[:-rem]
    C = C[:-rem]
    D = D[:-rem]

    A = np.reshape(A,(-1,128))
    B = np.reshape(B,(-1,128))
    C = np.reshape(C,(-1,128))
    D = np.reshape(D,(-1,128))

    for i in range(count):
        if np.max(A[i]) >= 0:#np.max(D[i])/2:
            sums[0] += A[i]
            events[0] += 1
        if np.max(B[i]) >= 0:#np.max(D[i])/2:
            sums[1] += B[i]
            events[1] += 1
        if np.max(C[i]) >= 0:# np.max(D[i])/2:
            sums[2] += C[i]
            events[2] += 1
        sums[3] += D[i]
        events[3] += 1

    for i in range(4):
        sums[i] /= events[i]


    plt.plot(sums[0],'g-')
    plt.plot(sums[1],'r-')
    plt.plot(sums[2],'b-')
    plt.plot(sums[3],'k-')
    plt.show()

    leg = legend[h['AcquisitionMode']]
    for i in range(4):
        print leg[i] + ":\t"+str(np.max(sums[i]))+\
            "\tcount:"+str(float(events[i])/events[3])


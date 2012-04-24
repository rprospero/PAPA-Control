from reader import PelFile
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

if __name__=='__main__':

    parser = OptionParser()

    parser.add_option("-X",action="store_true")
    parser.add_option("-Y",action="store_true")    

    (options,runs) = parser.parse_args()

    p1 = PelFile(basedir + "%04i/0001.pel"%int(runs[0]))
    p2 = PelFile(basedir + "%04i/0001.pel"%int(runs[1]))

    y1 = p1.data & 0x7FF
    y2 = p2.data & 0x7FF
    x1 = (p1.data & 0x3FF800) >> 11
    x2 = (p2.data & 0x3FF800) >> 11    

    if options.X:
        plt.hist(x1,bins=np.arange(512),histtype="stepfilled")
        plt.hist(x2,bins=np.arange(512),histtype="step")        
        plt.show()
    if options.Y:
        plt.hist(y1,bins=np.arange(512),histtype="stepfilled")
        plt.hist(y2,bins=np.arange(512),histtype="step")        
        plt.show()
        

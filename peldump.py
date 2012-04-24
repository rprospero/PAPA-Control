from reader import PelFile
from optparse import OptionParser
import numpy as np

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

if __name__=='__main__':

    parser = OptionParser()

    (options,runs) = parser.parse_args()

    p = PelFile(basedir + "%04i/0001.pel"%int(runs[0]))

    x = p.data & 0x7FF
    y = p.data & 0x3FF800 >> 11
    t = p.convertTime(p.data >> 32 & 0x7FFFFFFF)

    for i in range(len(x)):
        print "%i\t%i\t%f"%(x[i],y[i],t[i])

from reader import PelFile
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/%04i/"

if __name__=='__main__':

    parser = OptionParser() 
    parser.add_option("--run",action="store",type="int",default="2722")
    parser.add_option("--smooth",action="store",type="int",default="1")
    (options,runs) = parser.parse_args()  

    basedir = basedir%options.run

    gain = 5*(int(runs[0]))
    values = [int(i) for i in runs[1:]]

    subruns = np.array(values) + gain
    ps = [PelFile(basedir + "/%04i.pel"%r) for r in subruns]
    ys = [p.data & 0x7FF for p in ps]

    plt.hist(ys[0],bins=np.arange(512/options.smooth)*options.smooth,
             histtype="step",normed=True,color="red")
    plt.hist(ys[1],bins=np.arange(512/options.smooth)*options.smooth,
             histtype="step",normed=True)
    plt.show()
        

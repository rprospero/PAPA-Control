from reader import PelFile
from monfile import MonFile
import matplotlib.pyplot as plt
import Combiner
import numpy as np
from optparse import OptionParser
from Reduction import export

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

if __name__=='__main__':

    parser = OptionParser()

    parser.add_option("--mon",action="store",type="float",help="Minimum monitor value",default=8)
    parser.add_option("--run",action="store",type="int",help="Run number of run")

    parser.add_option("--xmin",action="store",type="int",help="Minimum x value",default=148)
    parser.add_option("--ymin",action="store",type="int",help="Minimum y value",default=223)
    parser.add_option("--xmax",action="store",type="int",help="Maximum x value",default=240)
    parser.add_option("--ymax",action="store",type="int",help="Maximum y value",default=302)
    parser.add_option("--out",action="store",type="string",help="Name for output file",default="out.dat")

    (options,name) = parser.parse_args()

    data = PelFile(basedir + "%04i/"%options.run + name[0] + ".pel")

    y,x = data.raw1d((options.xmin,options.ymin),(options.xmax,options.ymax))
    plt.plot(x[:-1],y)
    plt.show()

    np.savetxt(basedir + "%04i/"%options.run+options.out,
               np.asarray(np.transpose(np.vstack((x[:-1],y))),dtype=np.int32),
               fmt="%i")

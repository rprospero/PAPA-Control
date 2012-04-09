from reader import PelFile
from monfile import MonFile
import matplotlib.pyplot as plt
import Combiner
import numpy as np
from optparse import OptionParser


basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

def raw(run,name):
    p = PelFile(basedir+"%04i/" % run + name+".pel")
    mon = MonFile(basedir+"%04i/" % run + name+".pel.txt",False)
    val = np.sum(p.make3d()[:,:,50:100],axis=2)
    print val.shape
    spectrum_total = np.sum(mon.spec)
    return val/spectrum_total


def getf(w,x,y,z):

#    plt.plot(w,"r-",x,"g-",y,"b-",z,"k-")
#    plt.show()

    f = (-w+x+y-z)/(y-z)/2
    f = (1+f)/2
    f1 = (-w+x+y-z)/(x-z)/2
    f1 = (1+f1)/2

    return (f,f1,w)


if __name__=='__main__':

    parser = OptionParser()

    choices = {None:None,"flipper":0,"guides":1,"phase":2,"sample":3,"1":4,"2":5,"3":6,"4":7,"5":8,"6":9,"7":10,"8":11}

    parser.add_option("--mon",action="store",type="float",help="Minimum monitor value",default=8)
    parser.add_option("--vmin",action="store",type="float",help="Minimum efficiency value",default=0)
    parser.add_option("--cutoff",action="store",type="float",help="Minimum count rate",default=1e-6)    
    parser.add_option("--plot",action="store_true")
    parser.add_option("--save",action="store",type="string",help="File to save data")

    (options,runs) = parser.parse_args()

    runs = [int(x) for x in runs]


    w = raw(runs[-1],"w")

    f,f1,w = getf(w,
                raw(runs[-1],"x"),
                raw(runs[-1],"y"),
                raw(runs[-1],"z"))

    if options.plot:
        f[w<options.cutoff] = 0
        plt.spectral()
        #plt.gray()
        #plt.spring()
        plt.imshow(f,vmin=options.vmin,vmax=1)
        plt.show()

    if options.save:
        with open(options.save,"w") as outfile:
            outfile.write("x\ty\tcryo\tsolenoid\tintensity\n")
            for x in range(512):
                for y in range(512):
                    outfile.write("%i\t%i\t%e\t%e\t%e\n"%(x,y,f[x,y],
                                                          f1[x,y],
                                                          w[x,y]))

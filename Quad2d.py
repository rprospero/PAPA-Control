from reader import PelFile
from monfile import MonFile
import matplotlib.pyplot as plt
import Combiner
import numpy as np
from optparse import OptionParser
from QuadReduction import getf


basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

def raw(run,name,start=50,end=100):
    p = PelFile(basedir+"%04i/" % run + name+".pel")
    mon = MonFile(basedir+"%04i/" % run + name+
                  ".pel.txt",False)
    val = np.sum(p.make3d()[:,:,start:end],axis=2)
    print val.shape
    spectrum_total = np.sum(mon.spec)
    return val/spectrum_total,np.sqrt(val)/spectrum_total


if __name__=='__main__':

    parser = OptionParser()

    choices = {None:None,"flipper":0,"guides":1,
               "phase":2,"sample":3,"1":4,"2":5,
               "3":6,"4":7,"5":8,"6":9,"7":10,"8":11}

    parser.add_option("--mon",action="store",
                      type="float",
                      help="Minimum monitor value",
                      default=8)
    parser.add_option("--vmin",action="store",
                      type="float",
                      help="Minimum efficiency value",
                      default=0)
    parser.add_option("--cutoff",action="store",
                      type="float",
                      help="Minimum count rate",
                      default=1e-6)    
    parser.add_option("--plot",action="store_true")
    parser.add_option("--save",action="store",
                      type="string",
                      help="File to save data")
    parser.add_option("--start",action="store",
                      type="int",help="Beginning wavelength in 1/10 Angstrom units (e.g. 57 = 5.7 Angstoms).  The default value is 50",default=50)
    parser.add_option("--stop",action="store",
                      type="int",help="Ending wavelength in 1/10 Angstrom units (e.g. 57 = 5.7 Angstoms).  The default value is 100",default=100)
    parser.add_option("--display",action="store",
                      type="choice",
                      choices=["cryo","solenoid",
                               "instrument"],
                      default="cryo",
                      help="Whether to plot the " +
                      "efficiency of the cryo flipper,"+
                      "the solenoid"+
                      " flipper, or the instrument")

    (options,runs) = parser.parse_args()

    runs = [int(x) for x in runs]

    start=options.start
    stop=options.stop

    (w,dw) = raw(runs[-1],"w_new",start,stop)

    data= getf((w,dw),
               raw(runs[-1],"x_new",start,stop),
               raw(runs[-1],"y_new",start,stop),
               raw(runs[-1],"z_new",start,stop))

    f,df,f1,df1,papb,dpapb,n,dn = data

    if options.plot:
        if options.display=="cryo":
            plotdata=f
        if options.display=="solenoid":
            plotdata=f1
        if options.display=="instrument":
            plotdata=papb
        plotdata[w<options.cutoff] = 0
        plt.spectral()
        #plt.gray()
        #plt.spring()
        plt.imshow(plotdata,vmin=options.vmin,vmax=1)
        plt.show()

    if options.save:
        with open(options.save,"w") as outfile:
            outfile.write(
                "wave\tcryo\tcryoerr\tsolenoid\t"+
                "solenoiderr\tinstrument\t"+
                "instrumenterr\tintensity\n")
            for x in range(512):
                for y in range(512):
                    outfile.write(
                        ("%i\t%i\t%e\t%e\t%e\t%e\t"+
                         "%e\t%e\t%e\n")%
                        (x,y,f[x,y],df[x,y],
                         f1[x,y],df1[x,y],
                         papb[x,y],dpapb[x,y],
                         w[x,y]))

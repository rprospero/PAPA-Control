from reader import PelFile
from monfile import MonFile
import matplotlib.pyplot as plt
import Combiner
import numpy as np
from optparse import OptionParser
from QuadReduction import getf


basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

def raw(run,name,start=50,end=100,size=512):
    p = PelFile(basedir+"%04i/" % run + name+".pel")
    mon = MonFile(basedir+"%04i/" % run + name+
                  ".pel.txt",False)
    val = np.sum(p.make3d(size)[:,:,start:end],axis=2)
    print val.shape
    spectrum_total = np.sum(mon.spec)
    return val/spectrum_total,np.sqrt(val)/spectrum_total

def clean_data(out):
    out[np.isnan(out)]=0
    out[np.isposinf(out)]=1000
    out[np.isneginf(out)]=-1000    

if __name__=='__main__':

    parser = OptionParser()

    choices = {None:None,"flipper":0,"guides":1,
               "phase":2,"sample":3,"1":4,"2":5,
               "3":6,"4":7,"5":8,"6":9,"7":10,"8":11}

    parser.add_option("--vmin",action="store",
                      type="float",
                      help="Minimum efficiency value",
                      default=0)
    parser.add_option("--vmax",action="store",
                      type="float",
                      help="Maximum efficiency value",
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
                      choices=["off","on"],
                      default="on",
                      help="Whether to plot the cryoflipper" +
                      "in the off or on state")
    parser.add_option("--size",action="store",type="int",default=512,
                      help="Pixel resolution for rebinning.  Defaults to native 512x512 image.")

    (options,runs) = parser.parse_args()

    runs = [int(x) for x in runs]

    start=options.start
    stop=options.stop

    (w,dw) = raw(runs[-1],"w_new",start,stop,options.size)

    (x,dx) = raw(runs[-1],"x_new",start,stop,options.size)
    (y,dy) = raw(runs[-1],"y_new",start,stop,options.size)
    (z,dz) = raw(runs[-1],"z_new",start,stop,options.size)

    #w -> all flippers on
    #x -> cryo flipper on
    #y -> solenoid flipper on
    #z -> all flippers off

    off = (z-y)/(z+y)
    on = (w-x)/(w+x)

    if options.plot:
        if options.display=="off":
            plotdata=off
        if options.display=="on":
            plotdata=on
        plotdata[w<options.cutoff] = 0
        plt.spectral()
        #plt.gray()
        #plt.spring()
        plt.imshow(plotdata,vmin=options.vmin,vmax=1)
        plt.show()

    if options.save:
        with open(options.save,"w") as outfile:
            outfile.write(
                "x y on don cryo dcryo "+
                "solenoid dsolenoid off doff\n")
            [clean_data(x) for x in (f,df,f1,df1,papb,dpapb,w)]
            for i in range(512):
                for j in range(512):
                    outfile.write(
                        ("%i\t%i\t%e\t%e\t%e\t%e\t"+
                         "%e\t%e\t%e\n")%
                        (i,j,w[i,j],dw[i,j],
                         x[i,j],dx[i,j],
                         y[i,j],dy[i,j],
                         z[i,j],dz[i,j]))

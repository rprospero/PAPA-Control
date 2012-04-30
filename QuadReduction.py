from reader import PelFile
from monfile import MonFile
import matplotlib.pyplot as plt
import Combiner
import numpy as np
from optparse import OptionParser

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

def load(runs):
    paths = [basedir + "%04i/Manifest.xml"
             % run for run in runs]
    return Combiner.load(paths)


def export(runs,minmon=16):
    data = load(runs)

    keys = data.keys()

    base = basedir + "%04i/" % runs[-1]


    #phase(2) controls the cryo-flipper and sample(3) controls the
    #v-coil flipper
    #
    #w -> all flippers on
    #x -> cryo flipper on
    #y -> solenoid flipper on
    #z -> all flippers off
    w = [k for k in keys if float(k[2])<0
           and float(k[3])<0]
    y = [k for k in keys if float(k[2])<0
           and float(k[3])>0]
    x = [k for k in keys if float(k[2])>0
           and float(k[3])<0]
    z = [k for k in keys if float(k[2])>0
           and float(k[3])>0]
    print w
    print x
    print y
    print z
    if w != []:
        Combiner.save(base+"w_new.pel",
                      minmon,
                      w,
                      data)
    if x != []:
        Combiner.save(base+"x_new.pel",
                      minmon,
                      x,
                      data)
    if y != []:
        Combiner.save(base+"y_new.pel",
                      minmon,
                      y,
                      data)
    if z != []:
        Combiner.save(base+"z_new.pel",
                      minmon,
                      z,
                      data)

binning = 2

def rebin(x):
    return sum([x[i::binning] for i in range(binning)])

def rawspectrum(run,name,mins=(183,227),maxs=(234,302)):
    p = PelFile(basedir+"%04i/" % run + name+".pel")

    mon = MonFile(basedir+"%04i/" % run + name+".pel.txt",False)
    spectrum_total = np.sum(mon.spec)

    #get the data spectrum
    val = p.make1d(mins,maxs)
    val = rebin(val)
    err = np.sqrt(val)

    # get the background spectrum
    bval = p.make1d((412,412),(512,512))
    bval = rebin(bval)
    berr = np.sqrt(bval)

    #normalize background to beam size
    bval *= (maxs[0]-mins[0])/100*(maxs[1]-mins[1])/100
    berr *= (maxs[0]-mins[0])/100*(maxs[1]-mins[1])/100

    val -= bval

    err = np.sqrt(err**2+berr**2)

    val /= spectrum_total

    err = np.sqrt((err/spectrum_total)**2+
                  (err*np.sqrt(spectrum_total)/spectrum_total**2)**2)

    return (val,err)

def getf(ws,xs,ys,zs):
    (w,dw)=ws
    (x,dx)=xs
    (y,dy)=ys
    (z,dz)=zs

#    plt.plot(w,"r-",x,"g-",y,"b-",z,"k-")
#    plt.show()

    f = (x-w)/(y-z)
    f1 = (y-w)/(x-z)
    n = 2*(w*z-x*y)/(w+z-x-y)
    papb = (x-z)*(z-y)/(x*y-w*z)

    ymz = (y-z)**2
    wmx = (w-x)**2

    wterm = ymz*dw**2
    xterm = ymz*dx**2
    yterm = wmx*dy**2
    zterm = wmx*dz**2

    print "w contribution: %f"%(np.sqrt(np.sum(wterm))*1000)
    print "x contribution: %f"%(np.sqrt(np.sum(yterm))*1000)
    print "y contribution: %f"%(np.sqrt(np.sum(yterm))*1000)
    print "z contribution: %f"%(np.sqrt(np.sum(zterm))*1000)

    ferr = np.sqrt(wterm+xterm+yterm+zterm)/(y-z)**2

    f1err = np.sqrt(wterm+xterm+yterm+zterm)/(x-z)**2

    papberr=1/(x*y-w*z)**2*np.sqrt(((x-z)*(y-z)*z*dw)**2+
                                   ((w-y)*(y-z)*z*dx)**2+
                                   ((w-x)*(x-z)*z*dy)**2+
                                   (x*y*(x+y-2*z)+w*(-x*y+z**2)**2*dz**2))

    nerr = 2*np.sqrt((((x-z)*(y-z)*dw)**2+
                      ((w-y)*(y-z)*dx)**2+
                      ((w-x)*(x-z)*dy)**2+
                      ((w-x)*(w-y)*dz)**2)/
                     (w-x-y+z)**4)
                      

    return (f,ferr,f1,f1err,papb,papberr,n,nerr)

if __name__=='__main__':

    parser = OptionParser()

    choices = {None:None,"flipper":0,"guides":1,"phase":2,"sample":3,"1":4,"2":5,"3":6,"4":7,"5":8,"6":9,"7":10,"8":11}

    parser.add_option("-e","--export",action="store_true",help="Export into pel files")
    parser.add_option("--mon",action="store",type="float",help="Minimum monitor value",default=8)

    parser.add_option("--xmin",action="store",type="int",help="Minimum x value",default=104)
    parser.add_option("--ymin",action="store",type="int",help="Minimum y value",default=130)
    parser.add_option("--xmax",action="store",type="int",help="Maximum x value",default=428)
    parser.add_option("--ymax",action="store",type="int",help="Maximum y value",default=308)
    parser.add_option("--save",action="store",type="string",help="Save a data file")

    (options,runs) = parser.parse_args()

    runs = [int(x) for x in runs]

    if options.export:
        export(runs,options.mon)


    f,ferr,f1,f1err,papb,papberr,n,nerr = getf(rawspectrum(runs[-1],"w_new",(options.xmin,options.ymin),(options.xmax,options.ymax)),
                  rawspectrum(runs[-1],"x_new",(options.xmin,options.ymin),(options.xmax,options.ymax)),
                  rawspectrum(runs[-1],"y_new",(options.xmin,options.ymin),(options.xmax,options.ymax)),
                  rawspectrum(runs[-1],"z_new",(options.xmin,options.ymin),(options.xmax,options.ymax)))

    plt.errorbar(np.arange(0,20,0.1*binning),f,ferr,fmt="b*")
    plt.errorbar(np.arange(0,20,0.1*binning),f1,f1err,fmt="r-")
    plt.errorbar(np.arange(0,20,0.1*binning),papb,papberr,fmt="g+")
#    plt.plot(np.arange(0,20,0.1*binning),f1,"r-")
    plt.ylim(0,1)
    plt.show()

    if options.save:
        out = np.vstack((np.arange(0,20,0.1*binning),f,ferr,f1,f1err,papb,papberr,n,nerr))
        with open(options.save,"w") as outfile:
            outfile.write(
                "wave cryo cryoerr solenoid solenoiderr "+
                "instrument instrumenterr intensity internsityerr\n")
            out[np.isnan(out)]=0
            out[np.isposinf(out)]=1000
            out[np.isneginf(out)]=-1000
            np.savetxt(options.save, np.transpose(out))

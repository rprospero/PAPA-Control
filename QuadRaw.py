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

if __name__=='__main__':

    parser = OptionParser()

    parser.add_option("--xmin",action="store",type="int",help="Minimum x value",default=104)
    parser.add_option("--ymin",action="store",type="int",help="Minimum y value",default=130)
    parser.add_option("--xmax",action="store",type="int",help="Maximum x value",default=428)
    parser.add_option("--ymax",action="store",type="int",help="Maximum y value",default=308)
    parser.add_option("--save",action="store",type="string",help="Save a data file")

    (options,runs) = parser.parse_args()

    runs = [int(x) for x in runs]

    w,dw = rawspectrum(runs[-1],"w_new",(options.xmin,options.ymin),(options.xmax,options.ymax))
    x,dx = rawspectrum(runs[-1],"x_new",(options.xmin,options.ymin),(options.xmax,options.ymax))
    y,dy = rawspectrum(runs[-1],"y_new",(options.xmin,options.ymin),(options.xmax,options.ymax))
    z,dz = rawspectrum(runs[-1],"z_new",(options.xmin,options.ymin),(options.xmax,options.ymax))

    if options.save:
        out = np.vstack((np.arange(0,20,0.1*binning),w,dw,x,dx,y,dy,z,dz))
        with open(options.save,"w") as outfile:
            outfile.write(
                "wave ++ ++err -+ -+err "+
                "+- +-err -- --err\n")
            out[np.isnan(out)]=0
            out[np.isposinf(out)]=1000
            out[np.isneginf(out)]=-1000
            np.savetxt(outfile, np.transpose(out))

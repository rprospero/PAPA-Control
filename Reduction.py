from reader import PelFile
from monfile import MonFile
import matplotlib.pyplot as plt
import Combiner
import numpy as np
from optparse import OptionParser

from optparse import OptionParser

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

def load(runs):
    paths = [basedir + "%04i/Manifest.xml"
             % run for run in runs]
    return Combiner.load(paths)


def export(runs,sortby,flipper,minmon=16):
    data = load(runs)

    keys = data.keys()

    values = set([x[sortby] for x in keys])

    base = basedir + "%04i/" % runs[-1]

    for value in values:
        ups = [x for x in keys if x[flipper][0] != '-' 
               and x[sortby] == value]
        downs = [x for x in keys if x[flipper][0] == '-' 
                  and x[sortby] == value]
        Combiner.save(base+value+"up.pel",
                      minmon,
                      ups,
                      data)
        Combiner.save(base+value+"down.pel",
                      minmon,
                      downs,
                      data)
def spectrum(run,name,mins=(183,227),maxs=(234,302)):
    p = PelFile(basedir+"%04i/" % run + name+"up.pel")
    mon = MonFile(basedir+"%04i/" % run + name+"up.pel.txt",False)
    up = p.make1d(mins,maxs)/np.sum(mon.spec)
    p = PelFile(basedir+"%04i/" % run + name+"down.pel")
    mon = MonFile(basedir+"%04i/" % run + name+"down.pel.txt",False)
    down = p.make1d(mins,maxs)/np.sum(mon.spec)

    return (up-down)/(up+down)

def echoplot(run,names,mins=(148,223),maxs=(240,302),outfile=None):
    data = np.vstack(tuple([spectrum(run,name,mins,maxs) for name in names]))
    data[np.isnan(data)]=0
    data = data[:,0:100]
    xs = np.arange(100)*0.1
    ys = np.array([float(x) for x in names])
    plt.pcolor(xs,ys,data,vmin=-1,vmax=1)
    if outfile is None:
        plt.show()
    else:
        print name
        plt.savefig(outfile)
        plt.clf()

def echodiff(run,names,split,outfile=None):
    mins=(148,223)
    maxs=(240,302)
    data = np.vstack(tuple([np.arccos(spectrum(run,name,mins,(split,302))) - 
                            np.arccos(spectrum(run,name,(split,223),maxs)) for name in names]))

    data[np.isnan(data)]=0
    data = data[:,0:100]

    xs = np.arange(100)*0.1
    ys = np.array([float(x) for x in names])
    plt.pcolor(xs,ys,data,vmin=-1,vmax=1)
    if outfile is None:
        plt.show()
    else:
        print name
        plt.savefig(outfile)
        plt.clf()

if __name__=='__main__':

    parser = OptionParser()

    choices = {"flipper":0,"guides":1,"phase":2,"sample":3,"1":4,"2":5,"3":6,"4":7,"5":8,"6":9,"7":10,"8":11}

    parser.add_option("-e","--export",action="store_true",help="Export into pel files")
    parser.add_option("--sortby",action="store",type="choice",help="Which power supply is scanned",
                      choices=choices.keys())
    parser.add_option("--flip",action="store",type="choice",help="Which power supply runs the flipper",
                      choices=choices.keys())
    parser.add_option("--mon",action="store",type="float",help="Minimum monitor value",default=8)

    parser.add_option("--start",action = "store",type="float", help="The starting current of the scan")
    parser.add_option("--stop",action = "store", type="float", help="The ending current of the scan")
    parser.add_option("--step",action = "store", type="float", help="The current step of the scan")

    parser.add_option("--plot",action="store",type="choice",
                      help="Where to make a simple plot or perform a height diff",
                      choices=["plot","diff"],default="plot")

    (options,runs) = parser.parse_args()

    print options

    runs = [int(x) for x in runs]

    if options.export:
        export(runs,choices[options.sortby],choices[options.flip],options.mon)

    names = [str(x) for x in list(np.arange(options.start,options.stop,options.step))]

    if options.plot=="plot":
        echoplot(runs[-1],names)
    elif options.plot=="diff":
        echodiff(runs[-1],names,187)


from reader import PelFile
from monfile import MonFile
import matplotlib.pyplot as plt
import Combiner
import numpy as np

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
        Combiner.save(base+value+"down_temp.pel",
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
    xs = np.arange(200)
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
    data = np.vstack(tuple([np.abs(np.arccos(spectrum(run,name,mins,(split,302))) - 
                            np.arccos(spectrum(run,name,(split,223),maxs))) for name in names]))
    xs = np.arange(200)
    ys = np.array([float(x) for x in names])
    plt.pcolor(xs,ys,data,vmin=0,vmax=1)
    if outfile is None:
        plt.show()
    else:
        print name
        plt.savefig(outfile)
        plt.clf()

if __name__=='__main__':
#    export([2496],4,3,0.5)
    start = 4.75
    stop = 5.251
    step = 0.025
    names = [str(x) for x in list(np.arange(start,stop,step))]
    #
#    echoplot(2500,names,mins=(187,223),outfile='top.png')
#    echoplot(2500,names,maxs=(187,302),outfile='bottom.png')
#    echoplot(2496,names,mins=(187,223),outfile='top2496.png')
#    echoplot(2496,names,maxs=(187,302),outfile='bot2496.png')
    echodiff(2496,names,187)

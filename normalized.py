from reader import PelFile

import numpy as np
import os.path
from matplotlib import pyplot as plt
from monfile import MonFile

from optparse import OptionParser

def getState(run,name,state):
    base = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

    list =[i for i in os.listdir(base+str(run))
           if i.find(name)>=0 and i.find(".txt")==-1]

    if len(list)>1:
        print "I found the following files for the %s state:" % state
        print list
        print "I'm defaulting to %s" % list[0]
    return base+str(run)+"/"+list[0]

def spectrum(up,down,mins=(183,227),maxs=(234,302)):
    p = PelFile(up)
    mon = MonFile(up+".txt",False)
    up = p.make1d(mins,maxs)
    uperr = np.sqrt(up)
    up /= np.sum(mon.spec)
    uperr /= np.sum(mon.spec)
    p = PelFile(down)
    mon = MonFile(down+".txt",False)
    down = p.make1d(mins,maxs)
    downerr = np.sqrt(down)
    down /= np.sum(mon.spec)
    downerr /= np.sum(mon.spec)

    del p

    p = (up-down)/(up+down)
    e = 2 * up /(up**2-down**2)*np.sqrt(uperr**2+downerr**2)

    return (p,e)

if __name__=='__main__':

    parser = OptionParser()

    parser.add_option("-b","--blank",type='int',
                      help="Run number of blank run")
    parser.add_option("-s","--sample",type='int',
                      help="Run number of sample run")
    parser.add_option("-u","--up",help="Name of spin up file",default="up")
    parser.add_option("-d","--down",
                      help="Name of spin down file",default="down")

    (options,runs) = parser.parse_args()

    zup = getState(options.blank,options.up,"P0 spin up")
    zdown = getState(options.blank,options.down,"P0 spin down")
    sup = getState(options.sample,options.up,"P0 spin up")
    sdown = getState(options.sample,options.down,"P0 spin down")

    s,se = spectrum(sup,sdown)
    z,ze = spectrum(zup,zdown)

    y = np.log(s/z)/np.arange(0,20,0.1)**2
    ye = np.sqrt((se/s)**2+(ze/z)**2)/np.arange(0,20,0.1)**2

    plt.errorbar(np.arange(0,20,0.1),s/z,xerr=0,yerr=np.sqrt(ze**2+se**2))
    plt.ylim(0,2)
    plt.show()

#    plt.errorbar(np.arange(0,20,0.1),y,xerr=0,yerr=ye)
#    plt.show()

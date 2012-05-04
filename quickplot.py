import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/%04i/"

def rebin(x,bins=25):
    x = x[:50000]
    final = np.zeros(50000/bins)
    for b in range(bins):
        final += x[b::bins]
    return final

def up(run,export,bins,ut,dt):
    data = rebin(np.loadtxt((basedir%run)+"up_he.dat"),bins)
    if export: np.savetxt((basedir%run)+"up_he_rebin.dat",data)
    plt.plot(data/ut)
    plt.show()

def down(run,export,bins,ut,dt):
    data = rebin(np.loadtxt((basedir%run)+"down_he.dat"),bins)
    if export: np.savetxt((basedir%run)+"down_he_rebin.dat",data)
    plt.plot(data/dt)
    plt.show()

def both(run,export,bins,ut,dt):
    up = rebin(np.loadtxt((basedir%run)+"up_he.dat"),bins)
    down = rebin(np.loadtxt((basedir%run)+"down_he.dat"),bins)
    if export: np.savetxt((basedir%run)+"up_he_rebin.dat",up)    
    if export: np.savetxt((basedir%run)+"down_he_rebin.dat",down)
    up /= ut
    down /= dt
    plt.plot(up,"r-",down,"g-")
    plt.show()

def polar(run,export,bins,ut,dt):
    up = rebin(np.loadtxt((basedir%run)+"up_he.dat",dtype=np.float64),bins)
    down = rebin(np.loadtxt((basedir%run)+"down_he.dat",dtype=np.float64),bins)
    if export: np.savetxt((basedir%run)+"up_he_rebin.dat",up)    
    if export: np.savetxt((basedir%run)+"down_he_rebin.dat",down)
    up /= ut
    down /= dt
    plt.plot((up-down)/(up+down))
    plt.show()

if __name__=='__main__':

    parser = OptionParser()

    choices = {None:None,"up":up,"down":down,"both":both,"polar":polar}

    parser.add_option("--plot",action="store",type="choice",
                      help="Plot type: up,down,both, or polar",
                      choices=choices.keys())
    parser.add_option("--export",action="store_true",
                      help="Store rebinned data")
    parser.add_option("--bin",action="store",type="int",default=25,
                      help="Number of bins to group for rebinning")
    parser.add_option("--uptime",action="store",type="float",
                      help="Number of seconds measuring the up state")
    parser.add_option("--downtime",action="store",type="float",
                      help="Number of seconds measuring the down state")

    (options,run) = parser.parse_args()

    if options.plot:
        choices[options.plot](int(run[0]),options.export,options.bin,
                              options.uptime,options.downtime)

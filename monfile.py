"""Classes for dealing with neutron monitor data

This module contains a single class: MonFile.  This class is used to read
the time, intensity, and spectrum information out of a file produced
by the SNS's BMM_server

"""

import numpy as np
import re
import scipy.interpolate as ip
import matplotlib.pyplot as pyplot
from graphframe import GraphFrame

class MonFile:
    """Manages a file which holds neutron monitor data."""
    def __init__(self,file=None):
        """Creates a MonFile object"""
        self.time = None #The amount of time that the monitor ran.
        self.spec = None #The neutron spectrum detected on the monitor.
        if file is not None:
            self.load(file)

    def convertTime(self,t):
        """Converts a numpy array of time bins into neutron wavelengths"""
        t *= 50 #Convert time to microseconds
        distanceToG4 = 3.7338+2.5297
        #The distance between the end of G4 and the Helium 3 monitor.
        distanceToMonitor = 0.0 #FIXME
        t -= 860
        t *= 3.956034e-7/(distanceToMonitor+distanceToG4)/1e-10*1e-6*10 #The last 10 is to handle fractional angstroms
        return t

    def load(self,file):
        """Load data from the file given in the path string."""
        with open(file,"r") as infile:
            infile.readline() # drop first line
            line = infile.readline()
            #Find the time information
            m = re.search("lasted (\d+) milliseconds",line)
            if m:
                self.time = float(m.group(1))
            else:
                raise InvalidFileError
        data = np.loadtxt(file,dtype=np.float32,skiprows=3)
        x = data[:,0]
        y = data[:,1]
        y += 1
        x = self.convertTime(x)
        f = ip.interp1d(x,y) #Interpolation of neutron monitor
        xs = range(200)
        graph = GraphFrame(None,"Monitor")
        graph.plot(np.arange(0.0,20.0,0.1),f(xs))
        self.spec = np.expand_dims(np.expand_dims(f(xs),axis=0),axis=0)

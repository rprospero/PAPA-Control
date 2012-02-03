"""This module handles all neutron detection on SESAME"""

import __future__
from DetectorProcess import DetectorProcess
from Monitor import Monitor
from XMLConfig import XMLConfig

from time import clock,sleep
import logging

class Instrument:
    """This class handles the collection of normalized neutron data

    The class contains both a monitor object and a detector process
    to provide normalized monitor data

    """
    def __init__(self):
        """Create the instrument object"""
        self.mon = Monitor()
        self.det = DetectorProcess()
        self.running = False#is the detector running?
        self.starttime = clock()#When the most recent run started
        self.config = XMLConfig()
        self.det.directory(self.config.getDir())
        self.subrun=0

    def getPassword(self):
        return self.config.getPassword()

    def updateRunnumber(self):
        """Update to the next data run"""
        self.subrun=0
        runnumber = self.config.nextRun()

    def start(self):
        """Begin neutron collection"""
        self.subrun += 1
        logging.info("Starting run %d.%04d" % (self.config.getRunnumber(),self.subrun))
        self.det.runnumber(self.subrun)        
        self.det.directory(self.config.getDir())
        self.starttime = clock()        
        self.mon.startrun(self.subrun)
        self.det.start()

    def getMonitorFile(self):
        """Return the absolute path for the monitor file"""
        path = self.config.getDir()
        path += "%04dmon.txt"%(self.subrun)
        return path

    def getLocalMonitorFile(self):
        """Return the relative path for the monitor file"""
        return "%04dmon.txt"%(self.subrun)

    def getRunnumber(self):
        """Return the current run number"""
        return self.config.getRunnumber()

    def getPath(self):
        """Return the current directory for saved data"""
        return self.config.getDir()

    def stop(self):
        """End collection of neutrons"""
        self.mon.stoprun()
        self.det.stop()
        stop = clock()
        detector_count = self.det.count()
        monitor_count = self.mon.getCount()
        logging.info("Run %d.%04d ended" % (self.config.getRunnumber(),self.subrun))
        logging.info("Time:\t\t%f seconds"%(stop-self.starttime))
        logging.info("Detector:\t%d counts"%detector_count)
        logging.info("Monitor:\t%d counts"%monitor_count)
        with open(self.getMonitorFile(),"w") as stream:
                self.mon.localSave(stream,(clock()-self.starttime)*1000)
        return (stop-self.starttime,monitor_count,detector_count)

    def setParam(self,option,value):
        """Change the status of the detector"""
        self.det.setParam(option,value)

    def query(self,option):
        """Find the status of an instrument parameter"""
        return self.det.query(option)
        

    def timedrun(self,time):
        """Collect data for a set number of seconds"""
        self.start()
        sleep(time)
        self.stop()

    def __del__(self):
        """Destructor that handles the monitor login"""
        self.mon.logout()
        del self.mon
        del self.det

if __name__ == "__main__":
    i = Instrument()
    i.timedrun(10)
    i.timedrun(120)
    del i

"""This module handles the configuration of the Detector Software"""

import xml.dom.minidom
import os

class XMLConfig:
    """This object manages the file that stores the software configuration."""
    
    #Default path for the config file
    CONFIGFILE = 'C:/PAPA Control/trunk/config.xml'
    def __init__(self):
        """Loads the config file"""
        self.dom = xml.dom.minidom.parse(self.CONFIGFILE)
        dom = self.dom
        #Handle Run Number
        runnumber = dom.getElementsByTagName("Runnumber")
        if len(runnumber) != 1:
            raise RuntimeError("I do not understand having %d run numbers"%len(runnumber))
        runele = runnumber[0]
        #Current runnumber
        self.runnumber = int(runele.firstChild.nodeValue)
        #Handle Data Director
        directory = dom.getElementsByTagName("DataDirectory")
        if len(directory) != 1:
            print(directory)
            raise RuntimeError("I do not understand having %d directories"%len(runnumber))
        direle = directory[0]
        #Root directory for saving data runs
        self.dir = direle.firstChild.nodeValue

    def nextRun(self):
        """Updates the config file for the next data run"""
        self.runnumber += 1
        ele = self.dom.getElementsByTagName("Runnumber")[0]
        ele.firstChild.nodeValue = str(self.runnumber)
        with open(self.CONFIGFILE,"w") as stream:
            self.dom.firstChild.writexml(stream)
        return self.runnumber

    def getRunnumber(self):
        """Fetches the number of the current data run"""
        return self.runnumber

    def getDir(self):
        """Returns the directory of the current run"""
        path = self.dir+("%4d"%self.runnumber)+"/"
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def getPath(self):
        """Returns the root directory for saving data runs"""
        return self.dir

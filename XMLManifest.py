"""This module creates XML files to organize the subruns from the detector."""

import xml.etree.ElementTree as ET
import os
import os.path

class XMLManifest:
    """An XML file listing all of the subruns from a detector run"""
    def __init__(self,file,number):
        """Create a new XML manifest in a file with a run number"""
        if os.path.exists(file):
            self.load(file)
            return
        self.file=file
        self.root = ET.Element("Manifest")
        self.root.set("Run",str(number))
    
    def addRun(self,params):
        """Add a new subrun with a given dictionary of parameters"""
        subrun = ET.SubElement(self.root,"SubRun")
        subrun.set("number",str(params["subrun"]))
        subrun.set("start",str(params["start"]))
        subrun.set("time","%.2f"%params["time"])
        det = ET.SubElement(subrun,"Detector")
        det.set("count",str(params["detector count"]))
        det.set("path",str(params["detector file"]))
        mon = ET.SubElement(subrun,"Monitor")
        mon.set("count",str(params["monitor count"]))
        mon.set("path",str(params["monitor file"]))
        flip = ET.SubElement(subrun,"Flipper")
        flip.text = str(params["flipping current"])
        guide = ET.SubElement(subrun,"GuideFields")
        guide.text = str(params["guide current"])
        phase = ET.SubElement(subrun,"PhaseCoil")
        phase.text = str(params["phase current"])
        sample = ET.SubElement(subrun,"SampleCoil")
        sample.text = str(params["sample current"])
        for i in range(1,9):
            temp = ET.SubElement(subrun,"Triangle")
            temp.set("number",str(i))
            temp.text=str(params["triangle %d"%i])
        self.save()

    def load(self,file):
        """Read a manifest from a file"""
        tree = ET.parse(file)
        self.root = tree.getroot()
        self.file = file

    def save(self):
        """Save the manifest to a file"""
        tree = ET.ElementTree(self.root)
        tree.write(self.file)

    def getRuns(self,base=""):
        """Returns a list with each subrun node included."""
        return self.root.findall("SubRun")
        

if __name__ == "__main__":
    m = XMLManifest("temp.xml",0)
    m.addRun(1,29.99995,3,"1.txt",501,"1.pel")
    m.addRun(2,29.99995,3,"2.txt",520,"2.pel")
    m.addRun(3,29.99956,3,"3.txt",101,"3.pel")
    m.addRun(4,29.99959,3,"4.txt",454501,"4.pel")
    print(m.getRuns())

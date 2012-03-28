from reader import PelFile
from optparse import OptionParser

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

if __name__=='__main__':

    parser = OptionParser()

    (options,runs) = parser.parse_args()

    p = PelFile(basedir + "%04i/0001.pel"%int(runs[0]))
    d = p.header._asdict()
    for i in range(10):
        print "x%dGain\t%d" % (i,d["x%dGain"%i])
        print "y%dGain\t%d" % (i,d["y%dGain"%i])
    for i in ["strobeGain","EnergyGain","ThresholdGain"]:
        print "%s\t%d" % (i,d[i])

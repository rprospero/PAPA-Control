from reader import PelFile
from optparse import OptionParser

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

if __name__=='__main__':

    parser = OptionParser()

    (options,runs) = parser.parse_args()

    p1 = PelFile(basedir + "%04i/0001.pel"%int(runs[0]))
    d1 = p1.header._asdict()
    p2 = PelFile(basedir + "%04i/0001.pel"%int(runs[1]))
    d2 = p2.header._asdict()    
    
    for k in d1:
        if d1[k] != d2[k]:
            print str(k) + "\t" + str(d1[k]) + "\t" + str(d2[k])

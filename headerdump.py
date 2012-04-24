from reader import PelFile
from optparse import OptionParser

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

if __name__=='__main__':

    parser = OptionParser()

    (options,runs) = parser.parse_args()

    p = PelFile(basedir + "%04i/0001.pel"%int(runs[0]))
    d = p.header._asdict()
    keys = sort(d.keys())

    for k in keys:
        print str(k) + "\t" + str(d[k])

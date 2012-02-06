import os.path
from XMLManifest import XMLManifest
import sys
import matplotlib.pyplot as plt
import numpy as np

basedir = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

def history_load(path):
    base = os.path.dirname(basedir+"%04i/Manifest.xml"%path)
    manifest = XMLManifest(basedir+"%04i/Manifest.xml"%path,0)
    subruns = manifest.getRuns(base)
    counts = np.array([(float(subrun.find('Monitor').get('count'))/
               float(subrun.get('time'))) for subrun in subruns])
    errs = np.array([np.sqrt(float(subrun.find('Monitor').get('count'))/
               float(subrun.get('time'))) for subrun in subruns])
    plt.hist(counts,bins=50)#[0,1,26,27,28,29,30,31,32,33,34,35,36,37,38,50])
    plt.show()
    good = [x for x in counts if x >= 26 and x <=38]
    print np.mean(good)
    print np.std(good)
    print np.mean(errs[counts >= 20])

history_load(int(sys.argv[1]))

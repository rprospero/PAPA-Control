import reader
import numpy as np
import matplotlib.pyplot as plt
import sys

location = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/%04i/0001.pel"

legend = [['Energy','x9','y9','Strobe'],
          ['x8','x7','y7','Strobe'],
          ['y8','x6','y6','Strobe'],
          ['x5','x4','y4','Strobe'],
          ['y5','x3','y3','Strobe'],
          ['x2','x1','y1','Strobe'],
          ['y2','x0','y0','Strobe'],
          ['ADC A','ADC B','ADC C','ADC D'],
          ['Energy','x9','y9','Strobe']]

def extract(run):
    f = location%run
    p = reader.PelFile(f)

    return p.header

if __name__=="__main__":
    runs = []
    for i in range(2082,2210):
        
        try:
            h = extract(int(i))
            if h.AcquisitionMode > 8:

                runs.append((i,h.Month,h.Day,h.Year))
        except:
            print "Cannot open run %i"%i
            pass

    print runs

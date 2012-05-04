import reader
import numpy as np
import matplotlib.pyplot as plt

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
    plt.figure(figsize=(16,2))
    mode = 0

    with open("am8.html","w") as outfile:

        outfile.write("<html><body>\n")
        outfile.write("<table>\n")
        outfile.write("<tr><td>Run</td>")
        outfile.write("<td>Year</td>")
        outfile.write("<td>Month</td>")
        outfile.write("<td>Day</td></tr>")

        for run in range(1500,2300):
            try:
                h = extract(run)
            except:
                continue
            if h.AcquisitionMode == mode:
                print run
                outfile.write("<tr>")
                outfile.write("<td>%i</td>"%run)
                outfile.write("<td>%i</td>"%h.Year)
                outfile.write("<td>%i</td>"%h.Month)
                outfile.write("<td>%i</td>"%h.Day)
                outfile.write("</tr>\n")
        outfile.write("</table></body></html>")

import reader
import numpy as np
import matplotlib.pyplot as plt

location = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/2051/"

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
    f = location+"%04i.pel"%run
    p = reader.PelFile(f)
    bytes = np.fromfile(f,np.uint64,count=3000)[1280:]#[32:]
    A = bytes & 0x3FF
    B = (bytes>>10) & 0x3FF
    C = (bytes>>20) & 0x3FF
    D = (bytes >> 30) & 0x3FF
    
    return (p.header._asdict(),A,B,C,D)

if __name__=="__main__":
    plt.figure(figsize=(16,2))
    mode = -1

    with open(location+"gains.html","w") as outfile:

        outfile.write("<html><body>\n")
        outfile.write("<H2>AM0</H2><table>")

        for run in range(1,50):
            (h,A,B,C,D) = extract(run)
            plt.clf()
            plt.plot(A,'g-')
            plt.plot(B,'r-')
            plt.plot(C,'b-')
            plt.plot(D,'k-')
            plt.savefig(location+"%04i.png"%run,dpi=128)
            
            if h['AcquisitionMode'] != mode:
                mode = h['AcquisitionMode']
                print mode
                outfile.write("</table>\n"+
                              "<H2>AM%i</H2>\n"%mode+
                              "<table>\n"+
                              "<tr><td>gain</td>"+
                              "<td>green</td>"+
                              "<td>red</td>"+
                              "<td>blue</td>"+
                              "<td>image</td></tr>")

            labels = legend[mode]
            gains = [0,0,0,775]
            for i in range(3):
                if len(labels[i])==2: #Regular gain
                    gains[i] = h[labels[i]+'Gain']
                    print h[labels[i]+'Gain']
                    print "Gain: %i"%gains[i]
            
            outfile.write("<tr><td>%i</td><td>%s</td>"%(gains[1],labels[0])+
                          '<td>%s</td><td>%s</td><td><img src="file://%s" /></td></tr>'%(labels[1],labels[2],location+"%04i.png"%run))
        outfile.write("</table></body></html>")

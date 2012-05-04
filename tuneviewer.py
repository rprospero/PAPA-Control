import reader
import numpy as np
import matplotlib.pyplot as plt

location = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/2036/"

def gaingen():
    while True:
        for i in range(1,10):
            yield "x%iGain"%i
        for i in range(1,10):
            yield "y%iGain"%i

def extract(run):
    p = reader.PelFile(location+"%04i.pel"%run)
    image = np.sum(p.make3d(),axis=2)
    return (p.header._asdict(),image)

if __name__=="__main__":
    plt.figure(figsize=(4,4))
    g = gaingen()
    gain = g.next()
    old = -1000
    d={gain:{}}
    x = np.arange(512)

    for i in range(1,75):
        (h,im) = extract(i)
        plt.clf()
        plt.figimage(im,vmin=0,vmax=200,cmap="spectral")
        plt.savefig(location+"%04i.png"%i,dpi=128)
        plt.clf()
        plt.fill_between(x,np.sum(im,axis=0))
        plt.savefig(location+"x%04i.png"%i,dpi=128)
        plt.clf()
        plt.fill_between(x,np.sum(im,axis=1))
        plt.savefig(location+"y%04i.png"%i,dpi=128)
        if h[gain] < old: #we've moved on to the next gain
            print (gain,h[gain],old)
            gain = g.next()
            if not d.has_key(gain):
                d[gain] = {}
        d[gain][h[gain]] = i
        old = h[gain]
    with open(location+"gains.html","w") as outfile:
        outfile.write("<html><body>\n")
        for gain in d.keys():
            outfile.write("<H2>%s</H2>\n"%gain)
            outfile.write("<table><tr><td>Gain</td>\n")
            keys = d[gain].keys()
            keys.sort()
            for k in keys:
                print k
                outfile.write("<td>%i</td>\n"%k)
            outfile.write("</tr><tr><td>Image</td>\n")
            for k in keys:
                outfile.write('<td><img src="file://%s"</td>\n'%(location+"%04i.png"%d[gain][k]))
            outfile.write("</tr><tr><td>X</td>")
            for k in keys:
                outfile.write('<td><img src="file://%s"</td>\n'%(location+"x%04i.png"%d[gain][k]))
            outfile.write("</tr><tr><td>Y</td>")
            for k in keys:
                outfile.write('<td><img src="file://%s"</td>\n'%(location+"y%04i.png"%d[gain][k]))
            outfile.write("</tr></table>\n")
        outfile.write("</body></html>\n")

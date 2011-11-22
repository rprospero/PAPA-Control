from XMLManifest import XMLManifest
from XMLConfig import XMLConfig
import numpy as np
import os.path

def load(paths):
    
    currents = set([])#List of the configurations of the instrument
    runsets = {}#Directionary of lists of run nodes, indexed by their instrument configuration

    for path in paths:
        base = os.path.dirname(path)
        manifest = XMLManifest(path,0)
        subruns = manifest.getRuns(base)
        for subrun in subruns:
            triangles = sorted(subrun.findall('Triangle'),
                               key=lambda x:
                                   x.get('number'))
            current = (subrun.find('Flipper').text.strip(),
                       subrun.find('GuideFields').text.strip(),
                       subrun.find('PhaseCoil').text.strip(),
                       subrun.find('SampleCoil').text.strip(),
                       triangles[0].text.strip(),
                       triangles[1].text.strip(),
                       triangles[2].text.strip(),
                       triangles[3].text.strip(),
                       triangles[4].text.strip(),
                       triangles[5].text.strip(),
                       triangles[6].text.strip(),
                       triangles[7].text.strip())
            subrun.set("Base",base)
            if current in currents:
                runsets[current].append(subrun)
            else:
                currents.add(current)
                runsets[current]=[subrun]
    return runsets

def save(path,minmon,keys,runsets):
    runs = [x for key in keys for x in runsets[key]]
    mon = np.zeros((1001,),dtype=np.int32)
    tottime = 0
    totmon = 0
    totdet = 0
    with open(path,"wb") as pelfile:
        base = runs[0].get("Base")
        detpath=os.path.join(base,runs[0].find('Detector').get('path'))
        with open(detpath,"rb") as infile:
            header = np.fromfile(infile,dtype=np.int8,count=256)
            header.tofile(pelfile)
            del header
            #load the individual subruns
        for r in runs:
            base = r.get("Base")
            num = r.get('number')
            time = float(r.get('time'))
            moncount = int(r.find('Monitor').get('count'))
            detcount = int(r.find('Detector').get('count'))
            monpath = os.path.join(base,r.find('Monitor').get('path'))
            detpath = os.path.join(base,r.find('Detector').get('path'))
            if time <= 0 or moncount/time < minmon:
#                print("Dropping subrun %s as the count rate is too low"%num)
                continue
            tottime += time
            totmon += moncount
            totdet += detcount
            with open(monpath,"r") as infile:
                montemp = np.loadtxt(infile,dtype=np.int32,skiprows=3)
                #Handle old data, which has one fewer rows
                montemp = np.resize(montemp,(1001,2))
                mon += montemp[:,1]
            with open(detpath,"rb") as infile:
                infile.seek(256)
                dettemp = np.fromfile(infile,count=-1)
                dettemp.tofile(pelfile)
                del dettemp
    with open(path+".txt","w") as stream:
        stream.write("File Saved for Run Number %s.\n"%0)
        stream.write("This run had %d counts " % np.sum(mon))
        stream.write("and lasted %d milliseconds\n" % (float(tottime)*1000))
        stream.write("User Name=Unkown, Proposal Number=Unknown\n")
        for i in range(0,1000):
            stream.write("%d\t%d\n"%(i+1,mon[i]))

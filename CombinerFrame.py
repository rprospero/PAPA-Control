"""This module contains an application for combining runs files"""

from XMLManifest import XMLManifest
#from XMLConfig import XMLConfig
import wx
import numpy as np
import os.path

class CombinerFrame(wx.Frame):
    """This window is the main interaction point for combining runs"""
    def __init__(self,parent=None):
        """This method creates a CombinerFrame"""
        wx.Frame.__init__(self,parent,wx.ID_ANY,"Combine Data Runs")
        sizer = wx.GridBagSizer()

        self.runsets = {} #Dict of lists of Nodes for the subruns.
                          #The dict is indexed by current
                          #configuration

        #Create window contents
        self.listbox = wx.ListBox(self,-1,style=wx.LB_MULTIPLE,
                                  size=wx.Size(500,150))
        self.currentbox =  wx.ListBox(self,-1,style=wx.LB_MULTIPLE,
                                  size=wx.Size(500,150))
        addbutton = wx.Button(self,wx.ID_ADD)
        removebutton = wx.Button(self,wx.ID_REMOVE)
        loadbutton = wx.Button(self,wx.ID_OPEN)
        self.monctrl = wx.TextCtrl(self,-1,"8.0")
        combinebutton = wx.Button(self,wx.ID_SAVE)

        #Connect buttons to event handlers
        addbutton.Bind(wx.EVT_BUTTON,self.onAdd)
        removebutton.Bind(wx.EVT_BUTTON,self.onRemove)
        combinebutton.Bind(wx.EVT_BUTTON,self.onSave)
        loadbutton.Bind(wx.EVT_BUTTON,self.onLoad)


        #Add components to window
        sizer.Add(self.listbox,pos=wx.GBPosition(0,0),
                  flag=wx.EXPAND,span=wx.GBSpan(1,8))
        sizer.Add(addbutton,pos=wx.GBPosition(2,0),
                  flag=wx.EXPAND,span=wx.GBSpan(1,2))
        sizer.Add(removebutton,pos=wx.GBPosition(2,2),
                  flag=wx.EXPAND,span=wx.GBSpan(1,2))
        sizer.Add(self.currentbox,pos=wx.GBPosition(1,0),
                  flag=wx.EXPAND,span=wx.GBSpan(1,8))
        sizer.Add(wx.StaticText(self,-1,"Monitor Minimum: "),
                                    pos=wx.GBPosition(2,4),
                                    span=wx.GBSpan(1,1))
        sizer.Add(self.monctrl,pos=wx.GBPosition(2,5),flag=wx.EXPAND,
                  span=wx.GBSpan(1,1))
        sizer.Add(loadbutton,pos=wx.GBPosition(2,6),
                  flag=wx.EXPAND,span=wx.GBSpan(1,2))
        sizer.Add(combinebutton,pos=wx.GBPosition(3,0),
                  flag=wx.EXPAND,span=wx.GBSpan(1,8))        

        sizer.SetSizeHints(self)
        self.SetSizer(sizer)
        self.Show()

    def onAdd(self,event):
        """Add another manifest to be combined"""
        dlg=wx.FileDialog(self,"Choose the Manifest",
                          wildcard="SESAME manifest|Manifest.xml|Generic Manifest|*.xml",style=wx.FD_OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal()==wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                self.listbox.Insert(path,0)

    def onRemove(self,event):
        """Drop a manifest from the list"""
        indices = self.listbox.GetSelections()
        count=0 #How many files we've dropped thus far
        for i in indices:
            self.listbox.Delete(i-count)
            count+=1

    def onLoad(self,event):
        """Combine the manifests"""
        paths = self.listbox.GetItems()

        currents = set([])#List of the configurations of the instrument
        runsets = {}#Directionary of lists of run nodes, indexed by their instrument configuration

        #Get the subruns organized by flipper current
        for path in paths:
            base = os.path.dirname(path)
            print(base)
            manifest = XMLManifest(path,0)
            subruns = manifest.getRuns(base)
            print(subruns)
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
        for current in currents:
            self.currentbox.Insert(str(current),0)
        self.runsets = runsets

    def onSave(self,event):                           
        #Combine each flipper current
        dlg = wx.FileDialog(self,"Save PEL file",wildcard="PEL file|*.pel",
                            style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal()!=wx.ID_OK:
            return
        outfile = dlg.GetPath()

        minmon = float(self.monctrl.GetValue())#Monitor cutoff for live beam

        index = self.currentbox.GetSelections()
        keys = [eval(self.currentbox.GetItems()[i]) for i in index]

#        runlists = []
#        for key in keys:
#            runslists.join(self.runsets[key])

        runs = [x for key in keys for x in self.runsets[key]]

        print runs

        mon = np.zeros((1001,),dtype=np.int32)
        tottime = 0
        totmon = 0
        totdet = 0
        with open(outfile,"wb") as pelfile:
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
                    print("Dropping subrun %s as the count rate is too low"%num)
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
        with open(outfile+".txt","w") as stream:
            stream.write("File Saved for Run Number %s.\n"%0)
            stream.write("This run had %d counts " % np.sum(mon))
            stream.write("and lasted %d milliseconds\n" % (float(tottime)*1000))
            stream.write("User Name=Unkown, Proposal Number=Unknown\n")
            for i in range(0,1000):
                stream.write("%d\t%d\n"%(i+1,mon[i]))

if __name__=="__main__":
    app = wx.PySimpleApp()
    f = CombinerFrame()
    app.MainLoop()

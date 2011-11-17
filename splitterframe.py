"""This module splits a single run into multiple runs, depending on time and current"""

from XMLManifest import XMLManifest
import wx
import numpy as np
import os.path

path = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/"

def partition(l,n):
    length = len(l)
    print length
    print n
    print int(length/n)
    return [l[i*n:(i+1)*n] for i in range(int(length/n))]

class SplitterFrame(wx.Frame):
    """This windows is the main window of the program"""

    def __init__(self,parent=None):
        wx.Frame.__init__(self,parent,wx.ID_ANY,"Split Data Run")
        sizer = wx.GridBagSizer()

        self.runnumber = wx.TextCtrl(self,-1,"")
        self.time = wx.TextCtrl(self,-1,"60")

        save = wx.Button(self,wx.ID_SAVE)

        save.Bind(wx.EVT_BUTTON,self.onSave)

        sizer.Add(wx.StaticText(self,-1,"Run Number"),pos=wx.GBPosition(0,0),
                  flag = wx.EXPAND)
        sizer.Add(self.runnumber,pos=wx.GBPosition(0,1),
                  flag = wx.EXPAND)
        sizer.Add(wx.StaticText(self,-1,"Subruns to Combine"),pos=wx.GBPosition(1,0),
                  flag = wx.EXPAND)
        sizer.Add(self.time,pos=wx.GBPosition(1,1),
                  flag = wx.EXPAND)
        sizer.Add(save,pos=wx.GBPosition(2,0),
                  flag = wx.EXPAND,span=wx.GBSpan(1,2))

        sizer.SetSizeHints(self)
        self.SetSizer(sizer)
        self.Show()

    def onSave(self,event):
        """Split the data runs and save them to the disk"""

        run = int(self.runnumber.GetValue())

        directory = path+"%i/"%run

        m = XMLManifest(directory+"Manifest.xml",0)
        subruns = m.getRuns(directory)

        cutoff = int(self.time.GetValue())

        sets = partition(subruns,cutoff)

        print "Save!"

        for s,i in zip(sets,range(len(sets))):
            tottime = 0
            with open(directory+"Combined_%i_%i.pel"%(run,i),"wb") as outfile:
                head = np.fromfile(directory+s[0].find("Detector").get("path"),dtype=np.int8,count=256)
                head.tofile(outfile)
                
                mon = np.zeros((1001,),dtype=np.int32)
                
                for subrun in s:
                    tottime += float(subrun.get("time"))
                    with open(directory+subrun.find("Detector").get("path"),"rb") as infile:
                        infile.seek(256)
                        temp = np.fromfile(infile,count=-1)
                        temp.tofile(outfile)
                    with open(directory+subrun.find("Monitor").get("path"),"rb") as infile:
                        montemp = np.loadtxt(infile,dtype=np.int32,skiprows=3)
                        montemp = np.resize(montemp,(1001,2))
                        mon += montemp[:,1]
            with open(directory+"Combined_%i_%i.txt"%(run,i),"w") as outmon:                
                outmon.write("File Saved for Run Number "+str(run)+"_"+str(i)+".\n")
                outmon.write("This run had %d counts " % np.sum(mon))
                outmon.write("and lasted %d milliseconds\n" % (float(tottime)*1000))
                outmon.write("User Name=Unkown, Proposal Number=Unknown\n")
                for i in range(0,1000):
                    outmon.write("%d\t%d\n"%(i+1,mon[i]))

if __name__=="__main__":
    app = wx.PySimpleApp()
    f = SplitterFrame()
    app.MainLoop()

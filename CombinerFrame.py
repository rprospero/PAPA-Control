"""This module contains an application for combining runs files"""

from XMLManifest import XMLManifest
import Combiner
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

        runsets = Combiner.load(paths)

        currents = set(runsets.keys())


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

        Combiner.save(outfile,minmon,keys,self.runsets)

if __name__=="__main__":
    app = wx.PySimpleApp()
    f = CombinerFrame()
    app.MainLoop()

import __future__
import ctypes
import numpy
import struct
import json

nidaq = ctypes.windll.nicaiu #Link to nicaiu.dll

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32


DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByChannel = 0

#List of which tasks control the triangles
triangles = ["AnalogOutHighBlank",
             "AnalogOut3",
             "AnalogOut4",
             "AnalogOut6",
             "AnalogOut5",
             "AnalogOut2",
             "AnalogOut1",
             "AnalogOutLowBlank"]

#Dictionary of tasks which contorl small supplies
supplies = {"flipper":"AnalogOut7",
            "phase":"AnalogOut8",
            "guides":"AnalogOut9",
            "sample":"AnalogOut10"}


def compensate(value,f):
    return value*f['m']+f['b']

class PowerSupply:
    
    def __init__(self):

        self.triangleHandles = []
        self.supplyHandles = {}

        self.values = {}

        for t in triangles:
            taskHandle = TaskHandle(0) 
            self.CHK(nidaq.DAQmxLoadTask(t,
                              ctypes.byref( taskHandle )))
            self.triangleHandles.append(taskHandle)
            self.triangle
        for (k,v) in supplies.items():
            taskHandle = TaskHandle(0)
            self.CHK(nidaq.DAQmxLoadTask(v,
                              ctypes.byref( taskHandle )))
            self.supplyHandles[k] = taskHandle
            
        print self.supplyHandles

        with open("calibration.json") as configFile:
            self.calibration = json.load(configFile)

        self.values['triangles'] = [0]*8
        for i in range(1,9):
            self.triangle(i,0)
        self.flipper(0)
        self.guides(0)
        self.phase(0)
        self.sample(0)
            

    def set(self,task,x):
        """Takes a task handle and a current and sets that task to that current."""
        self.CHK(nidaq.DAQmxWriteAnalogScalarF64( task,
                                                  True,
                                                  float64(1.0),
                                                  float64(x), #Voltage
                                                  None))

    def triangle(self,tri,curr):
        self.set(self.triangleHandles[tri-1],
                 compensate(curr,self.calibration['triangles'][tri-1]))
        self.values['triangles'][tri-1]=curr
        return self.getTriangle(tri)

    def getTriangle(self,tri):
        return self.values['triangles'][tri-1]

    def flipper(self,curr):
        self.set(self.supplyHandles["flipper"],
                 compensate(curr,self.calibration['flipper']))
        self.values['flipper']=curr
        return self.getFlipper()
    def getFlipper(self):
        return self.values['flipper']
    
    def guides(self,curr):
        self.set(self.supplyHandles["guides"],
                 compensate(curr,self.calibration['guides']))
        self.values['guides']=curr
        return self.getGuides()
    def getGuides(self):
        return self.values['guides']
    def phase(self,curr):
        self.set(self.supplyHandles["phase"],
                 compensate(curr,self.calibration['phase']))
        self.values['phase']=curr
        return self.getPhase()
    def getPhase(self):
        return self.values['phase']
    def sample(self,curr):
        self.set(self.supplyHandles["sample"],
                 compensate(curr,self.calibration['sample']))        
        self.values['sample']=curr
        return self.getSample()
    def getSample(self):
        return self.values['sample']

    def CHK( self, err ):
        """a simple error checking routine"""
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))
                
    def stop( self ):
        for task in self.triangleHandles:
            self.set(task,0)
            nidaq.DAQmxStopTask( task )
            nidaq.DAQmxClearTask( task )
        for task in self.supplyHandles:
            self.set(task,0)
            nidaq.DAQmxStopTask( task )
            nidaq.DAQmxClearTask( task )
            
    def __del__(self):
        self.stop()



if __name__=="__main__":
    x=PowerSupply()


"""This module contains code to talk with the Lexitech PAPA detector."""

import __future__
import ctypes
import numpy
import serial
import re
import struct
import datetime
from time import clock,sleep
from math import sqrt
nidaq = ctypes.windll.nicaiu #Link to nicaiu.dll

#typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32

def dualextract(vals):
    """Extracts two comma separated numbers from a string"""
    m = re.match('([-+]?\d+),([-+]?\d+)',vals)
    if m is None:
        raise RuntimeException('Invalid pair value')
    (a,b) = m.groups()
    return (int(a),int(b))

#List of the parameters that can be read from the PAPA
#This should probably be converted to a dictionary at some point
serialReads = [#Data Acquisition
             ('shutter','?SO\r',True,int),
             ('mode','?AM\r',True,int),
             ('pulse strobe','?PS\r',True,int),
             ('gate capture','?GC\r',True,int),
             ('reset timer polarity','?RT\r',True,int),
             #High voltage supplies
             ('power supply voltage','?PV\r',True,int),
             ('pmt power supply state','?PE\r',True,int),
             ('energy pmt power supply voltage','?EV\r',True,int),
             ('energy pmt power supply state','?EE\r',True,int),
             ('intensifier power supply voltage','?IV\r',True,int),
             ('intensifier power supply state','?IE\r',True,int),
             #Event Discrimination
             ('trigger thresholds','?TE\r',True,dualextract),
             ('end event fraction for energy','?TF\r',True,int),
             ('trigger thresholds for papa strobe','?TP\r',True,dualextract),
             ('end event fraction for papa strobe','?TQ\r',True,int),
             ('coincidence timer lead and lag','?CT\r',True,dualextract),
             #Digital Signal Processing
             ('offset for ADC channel A','?OA\r',True,int),
             ('offset for ADC channel B','?OB\r',True,int),
             ('offset for ADC channel C','?OC\r',True,int),
             ('offset for ADC channel D','?OD\r',True,int),
             ('channel A filter','?FA\r',True,int),
             ('channel D filter','?FD\r',True,int),
             ('gray constant','?BA\r',True,int),
             ('bit shift','?BS\r',True,int),
             #Temperature Control
             ('temperature set point for zone zero','?TS0\r',True,int),
             ('temperature set point for zone one','?TS1\r',True,int),
             ('kp gain for zone zero','?KP0\r',True,int),
             ('kp gain for zone one','?KP1\r',True,int),
             ('ki for zone zero','?KI0\r',True,int),
             ('ki for zone one','?KI1\r',True,int),
             ('kd for zone zero','?KD0\r',True,int),
             ('kd for zone one','?KD1\r',True,int),
             ('temperature for zone zero','?TC0\r',True,int),
             ('temperature for zone one','?TC1\r',True,int),
             #Analog Channel Gains And Settings
             ('gain for X0','?GX0\r',True,int),
             ('gain for X1','?GX1\r',True,int),
             ('gain for X2','?GX2\r',True,int),
             ('gain for X3','?GX3\r',True,int),
             ('gain for X4','?GX4\r',True,int),
             ('gain for X5','?GX5\r',True,int),
             ('gain for X6','?GX6\r',True,int),
             ('gain for X7','?GX7\r',True,int),
             ('gain for X8','?GX8\r',True,int),
             ('gain for X9','?GX9\r',True,int),
             ('gain for Y0','?GY0\r',True,int),
             ('gain for Y1','?GY1\r',True,int),
             ('gain for Y2','?GY2\r',True,int),
             ('gain for Y3','?GY3\r',True,int),
             ('gain for Y4','?GY4\r',True,int),
             ('gain for Y5','?GY5\r',True,int),
             ('gain for Y6','?GY6\r',True,int),
             ('gain for Y7','?GY7\r',True,int),
             ('gain for Y8','?GY8\r',True,int),
             ('gain for Y9','?GY9\r',True,int),
             ('gain for strobe pmt','?GS\r',True,int),
             ('gain for energy pmt','?GE\r',True,int),
             ('gain for threshold channel','?GT\r',True,int),
             ('ADC offset voltage','?AV\r',True,int),
             #Miscellaneous
             ('serial number','?SN\r',True,int),
             ('version','?VS\r',False,str)]

#A dictionary of the serial commands needed to control the PAPA detector
#Each tuple takes the command, followed by the number of arguments
#See the Lexitech PAPA Hardware Manual for descriptions of the serial commands
serialWrites = {#Data Acquisition
             'shutter':('SO',1),
             'mode':('AM',1),
             'pulse strobe':('PS',1),
             'gate capture':('GC',1),
             'reset timer polarity':('RT',1),
             #High voltage supplies
             'power supply voltage':('PV',1),
             'pmt power supply state':('PE',1),
             'energy pmt power supply voltage':('EV',1),
             'energy pmt power supply state':('EE',1),
             'intensifier power supply voltage':('IV',1),
             'intensifier power supply state':('IE',1),
             #Event Discrimination
             'trigger thresholds':('TE',2),
             'end event fraction for energy':('TF',1),
             'trigger thresholds for papa strobe':('TP',2),
             'end event fraction for papa strobe':('TQ',1),
             'coincidence timer lead and lag':('CT',2),
             #Digital Signal Processing
             'offset for ADC channel A':('OA',1),
             'offset for ADC channel B':('OB',1),
             'offset for ADC channel C':('OC',1),
             'offset for ADC channel D':('OD',1),
             #Temperature Control
             'kp gain for zone zero':('KP0',1),
             'kp gain for zone one':('KP1',1),
             'ki for zone zero':('KI0',1),
             'ki for zone one':('KI1',1),
             #Analog Channel Gains And Settings
             'gain for X':('GX',2),
             'gain for Y':('GY',2),
             'gain for strobe pmt':('GS',1),
             'gain for energy pmt':('GE',1),
             'gain for threshold channel':('GT',1),
             'ADC offset voltage':('AV',1)}
    

def CHK(err):
    """a simple error checking routine

    This function checks the result of any of the DAQmx system calls.
    If the system call succeeded, it returns nothing.  If the call failed,
    this function throws and exception with a description of the error.
    It currently throws a RuntimeError, but there may be a better error type
    to throw.

    """
    if err == -200284:
        return
    if err < 0:
        buf_size = 500
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

class Detector:
    """An object which interfaces with the PAPA detector"""
    #constants
    DAQmx_Val_ChanPerLine=0   # One Channel For Each Line
    DAQmx_Val_ChanForAllLines=1   # One Channel For All Lines

    DAQmx_Val_GroupByChannel=0  # Group by Channel (Not Interleaved)
    DAQmx_Val_GroupByScanNumber=1   # Group by Scan Number (Interleaved)

    DAQmx_Val_Rising=10280 # Rising
    DAQmx_Val_Falling=10171 # Falling

    DAQmx_Val_FiniteSamps = 10178 # Finite Samples
    DAQmx_Val_ContSamps = 10123 # Continuous Samples
    DAQmx_Val_HWTimedSinglePoint = 12522 # Hardware Timed Single Point

    Insufficient_Points_Error = -200284 #The error code when there aren't enough
                                        #data points.  This isn't the official name.
    HARDWARE_BUFFER = uInt64(100000)#Memory buffer for holding incoming data

    baseDirectory = 'C:/Documents and Settings/sesaadmin/My Documents/'

    def __init__(self,count=1000):
        "Creates a new Detector object.  Only one should exist at a time"""
        taskHandle = TaskHandle(0)
        
        self.taskHandle=taskHandle#NIDAQmx task
        self.count=count#maximum number of data points to read
        #Serial port connection to PAPA
        self.ser = serial.Serial(port='COM1',baudrate=19200,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=0)
        self.running = False#Are we taking data?
        self.getStatus()
        self.powerOn()

    def powerOn(self):
        self.setParam('pmt power supply state',1)        
        self.setParam('energy pmt power supply state',1)
        self.setParam('intensifier power supply state',1)
#        self.setParam('mode',12)

#While the Gerard is looking at the energy PMT, let's not try and supply it with power        
#        self.setParam('energy pmt power supply state',0)        


    def powerOff(self):
        self.setParam('pmt power supply state',0)
        self.setParam('energy pmt power supply state',0)
        self.setParam('intensifier power supply state',0)

    def start(self):
        """Start the data aquisition process"""
        if self.running:
            return
        taskHandle = self.taskHandle
        #Need to create a new task for each DAQ to keep the buffer clean
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))
        self.taskHandle=taskHandle
        #Add a digital channel to our task to read data from PAPA
        CHK(nidaq.DAQmxCreateDIChan(taskHandle,"Dev1/port0:3","",
                                    self.DAQmx_Val_ChanForAllLines))
        #Use handshaking to tell the detector to send more data.
        CHK(nidaq.DAQmxCfgHandshakingTiming(taskHandle,
                                            self.DAQmx_Val_ContSamps,
                                            self.HARDWARE_BUFFER))
        CHK(nidaq.DAQmxStartTask(self.taskHandle))
        self.ser.write('AS1\r')#Tell the detector to start sending data
        sleep(0.1)
        response = self.ser.read(80)
        if response != 'AS1\rOK\r':
            logging.error( response)
            raise RuntimeError('Could not start data acquisition')
        self.running=True

    def stop(self):
        """End the data acquisition process"""
        if not self.running:
            return
        CHK(nidaq.DAQmxStopTask(self.taskHandle))
        self.ser.write('AS0\r')#Tell the detector to stop taking data
        sleep(0.1)
        response = self.ser.read(80)
        self.running=False

    def clear(self):
        """Free the resources used by our task"""
        CHK(nidaq.DAQmxClearTask(self.taskHandle))

    def getStatus(self):
        """Read all of the current parameters from the detector"""
        r = self.ser.read
        w = self.ser.write
        st = 0.1 #sleep time
        d = {} #Dictionary for storing parameters

        #read mainboard commands
        for name,command,ok,form in serialReads:
            w(command)
            sleep(st)
            t = r(80)
            length = len(command)
            if t[0:length]==command:
                if ok:
                    t=form(t[length+2:-1])
                else:
                    t=form(t[length:-1])
            else:
              raise RuntimeError('Command \'%s\' not recognized!' % command)
            d[name]=t

        #read the lens focus position
        w('LC\r')
        sleep(st)
        t=r(80)
        if t!='LC\r':
            raise RuntimeError('Failed to connect to camera lens controller')
        attempts = 0
        while(attempts<10):
            w('PF\r')
            sleep(st)
            t=r(80)
            if t[:6]=='PF\rOK\r':
                t=t[6:-1]
                break
            attempts += 1
        if attempts == 10:
            raise RuntimeError('Failed to connect to camera lens controller after ten attempts')
        d['lens focus position']=int(t)
        w('*\r')
        sleep(st)
        t=r(80)
        
        self.status=d

    def makeHeader(self):
        """Turn the status information into a .pel file header

        The structure of this header can be found in the Lexitech PAPA
        Imager software manual.  Note that, since the commands to read
        some of these values are undocumented, the values themselves
        have been hard coded to our best estimations.

        """
        header = b'.pel'
        s = self.status
        p = struct.pack
        if s['mode']==14:
            bps = 8
        else:
            bps=4
        header += p('<BBBBBBBBH',0,1,3,bps,1,0,1,1,
                              s['lens focus position'])
        header += p('<40s',s['version'])
        header += p('<HBB',3,9,1)#Product Number,Bits per coordinate,Energy
        header += p('<BHBBB',1,75,4,7,0)#Timing,ADClockFreq,Firmware Maj/Min/Beta
        header += p('<HBI',s['serial number'],s['mode'],3604403926)#Mode Capability
        header += p('<BH',s['shutter'],s['power supply voltage'])
        header += p('<HHHH',61536,0,65531,64513)#power supply gains
        header += p('<B',s['pmt power supply state'])
        header += p('<H',s['energy pmt power supply voltage'])
        header += p('<HHHH',63536,0,65531,64513)#energy pmt gains
        header += p('<B',s['energy pmt power supply state'])
        header += p('<H',s['intensifier power supply voltage'])
        header += p('<HHHH',63536,0,5,0)#intensifier gains
        header += p('<B',s['intensifier power supply state'])
        for i in range(10):
            header += p('<H',s['gain for X%d'%i])
        for i in range(10):
            header += p('<H',s['gain for Y%d'%i])
        header += p('<HH',s['gain for strobe pmt'],s['gain for energy pmt'])
        header += p('<H',s['gain for threshold channel'])
        header += p('<H',s['ADC offset voltage'])
        for i in ['A','B','C','D']:
            header += p('<h',s['offset for ADC channel '+i])
        header += p('<HH',s['trigger thresholds for papa strobe'][0],s['trigger thresholds'][1])
        header += p('<H',s['end event fraction for papa strobe'])
        header += p('<HH',s['trigger thresholds'][0],s['trigger thresholds'][1])
        header += p('<H',s['end event fraction for energy'])
        header += p('<BB',s['channel A filter'],s['channel D filter'])
        header += p('<BB',s['gate capture'],s['reset timer polarity'])
        header += p('<h',s['coincidence timer lead and lag'][0])
        header += p('<h',s['coincidence timer lead and lag'][1])
        header += p('<BB',s['gray constant'],s['bit shift'])
        header += p('<H',s['temperature set point for zone zero'])
        header += p('<H',s['temperature set point for zone one'])
        header += p('<H',s['kp gain for zone zero'])
        header += p('<H',s['kp gain for zone one'])
        header += p('<H',s['ki for zone zero'])
        header += p('<H',s['ki for zone one'])
        header += p('<H',s['kd for zone zero'])
        header += p('<H',s['kd for zone one'])
        header += p('<H',s['temperature for zone zero'])
        header += p('<H',s['temperature for zone one'])
        header += p('<H39x',s['pulse strobe'])
        today = datetime.datetime.now()
        header += p('<HHH',today.year,today.month,today.day)
        header += p('<HHH',today.hour,today.minute,today.second)
        return header

    def getCountRate(self):
        """Count for ten seconds and get the number of counts per second."""
        (num,_)=self.read(100000,10)
        return num/10

    def __del__(self):
        """Destructor for the detector object"""
        logging.info("Task Stopped")
        self.powerOff()
        self.ser.close()        
        if self.taskHandle.value != 0:
            if self.running:
                self.stop()
            nidaq.DAQmxClearTask(self.taskHandle)

    def read(self,count=1000,time=0.1):
        """Returns a given number of data points, with a specified timeout"""
        points = int32() #location to store the number of data points read in from NI card.
        data = numpy.zeros((count,),dtype=numpy.uint32)
        err = nidaq.DAQmxReadDigitalU32(self.taskHandle,count,float64(time),
                                      self.DAQmx_Val_GroupByChannel,data.ctypes.data,
                                      count,ctypes.byref(points),None)
        if err < 0 and err != self.Insufficient_Points_Error:
            CHK(err)
        num = points.value
        return (num,data)

    def flush(self):
        """Attempts to empty the buffer. <em>This code is deprecated</em>"""
        points = int32() #location to store the number of data points read in from NI card.
        data = numpy.zeros((1,),dtype=numpy.uint32)
        err = nidaq.DAQmxReadDigitalU32(self.taskHandle,-1,float64(0.1),
                                      self.DAQmx_Val_GroupByChannel,data.ctypes.data,
                                      1,ctypes.byref(points),None)#Read the whole buffer
        if err < 0 and err != self.Insufficient_Points_Error:
            CHK(err)
        num = points.value
        return (num,data)
        

    def setParam(self,param,val):
        """Adjusts a given state variable of the detector to a new value."""
        #get the command and number of arguments
        (command,argc) = serialWrites[param]
        #parse the arguments into a byte string
        if argc == 1:
            command += bytes(val)
        elif argc == 2:
            command += bytes(val[0])+b','+bytes(val[1])
        command += b'\r'
        self.ser.write(command)
        sleep(0.1)
        t = self.ser.read(80)
        if t!=command+b'OK\r':
            logging.error(t)
            raise RuntimeError('Failed to set %s' % param)
        logging.debug( command)
        logging.debug( t)
        if(param[:10] == "gain for X" or param[:10] == "gain for Y"):
            param += str(val[0])
            val = val[1]
            logging.debug( param)
            logging.debug( val)
        self.status[param]=val
        return

    def printStatus(self):
        """Display's the detector's current parameters"""
        for k in self.status.keys():
            logging.info("%s:\t%s"%(k,str(self.status[k])))

    def collect(self,runNumber,time):
        """Saves data to a file.  <em>This command is deprecated</em>"""
        now = datetime.datetime.now()
        f = self.baseDirectory # file for saving
        f += str(runNumber)
        f += " - " + "%02d%02d%4d.pel"%(now.month,now.day,now.year)
        x.printStatus()
        logging.info("Collecting data...")
        with open(f,"wb") as stream:
            stream.write(self.makeHeader())
            start = clock()
            self.start()
            #self.flush()            
            count=0
            reads = 240000
            while((clock()-start) < time):
                try:
                    (num,data)=self.read(reads)
                except RuntimeError, (err):
                    logging.error("Count:%d\tTime:%f"%(count,clock()-start))
                    logging.error(err)
                    break
                count += num
                if num < reads:
                    data = data[:num]
                stream.write(data.tostring())
                if num < reads:
                    sleep(0.01)
                else:
                    sleep(0.01)
            t = clock()-start
            self.stop()
        count //= 2
        logging.info("Collected %d neutrons in %d seconds" % (count,t))
        logging.info("Count rate is %f +/- %f" % (count/float(t),sqrt(count)/float(t)))

            
                

if __name__=="__main__":
    x=Detector()
    try:
##        runnumber = 1144
##        gain = 300
##        x.setParam('gain for energy pmt',300)
##        x.collect(runnumber,1)
##        while(gain <= 500):
##            x.setParam('gain for energy pmt',gain)
##            x.status['gain for energy pmt']
##            sleep(1)            
##            print("Run\t%d\t\tEnergy Gain\t%d"%(runnumber,gain))
##            x.collect(runnumber,2228)
##            runnumber += 1
##            gain += 10
        runnumber=10193
#        x.setParam('gain for energy pmt',460)
        x.collect(runnumber,1)
        while runnumber < 10194:
            print("\n\nStarting Run # %d"%(runnumber))
            x.collect(runnumber,6)
            print("Finished Run # %d\n\n--------------------"%(runnumber))
            runnumber += 1
    finally:
        del x

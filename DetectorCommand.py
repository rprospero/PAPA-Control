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

ser = serial.Serial(port='COM1',baudrate=19200,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=0.05)

print("\n\n**************************************\n\n"\
      "-----   Detector Command Center  -----\n\n"\
      "**************************************\n\n")
Cmdq = 0
while Cmdq==0:
    Choice=0
    try:
        sleep(1)
        Choice = input("\n--------------------------------------------\n"\
                       "1)Send Command\n2)Command List\n3)Quit\n\n"\
                       "8)Activate Power Supplies\n9)Kill Power Supplies\n"\
                       "----------------------------------------------\n")
    except (NameError,SyntaxError):
        print("\nOops! Unrecognized Command.  Try again...")
        sleep(.5)
    finally:       
        if Choice==1:
            Cmd = raw_input("\nEnter command to send:  ")
            ser.write(Cmd+"\r")
            sleep(.1)
            strReturn=ser.read(100)
            print("\nResponse from Detector:  " +
                  strReturn.lstrip(Cmd+"\rOK").rstrip("\r"))
        elif Choice==2:
            print("\nDATA ACQUISITION\n"\
                  "\"SOb\"  {b: 0=Closed, 1=Open}\n"\
                  "\"?SO\"  Shutter Stauts\n"\
                  "...\n")
        elif Choice==3:
            Cmdq=1
        elif Choice==8:
            ser.write("PE1\r")
            ser.write("EE1\r")
            ser.write("IE1\r")
            ser.read(100)
        elif Choice==9:
            ser.write("PE0\r")
            ser.write("EE0\r")
            ser.write("IE0\r")
            ser.read(100)
            
ser.close()
del ser
          
    
      

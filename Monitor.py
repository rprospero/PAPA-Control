"""This module contains a class for controlling the He3 Monitor"""

import socket
import struct
import numpy as np

from time import sleep


class Monitor:
    """This class interfacts with BMMserver to control the He3 monitor"""
    HOST = '192.168.70.56' #the ip address of the BMMserver

    #These ports are setup in BMMserver.
    SENDPORT = 8003 #the port to send commands
    RECVPORT = 8001 #the port to receive responses to commands
    HISTPORT = 8005 #the port on which to receive histogram data

    #The constants are the values expected in the packets by BMMserver
    GETBMHISTODATA = 0x513
    STARTALL = 0x100
    STOPALL = 0x101
    LOGIN = 0x10
    LOGOUT = 0x11
    ECHO = 0x12
    SAVEDATA = 0x201

    MONTOF = b'diiiii?i'

    def __init__(self):
        """Create a connection to the monitor computer"""
        #create the sending socket
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        #create the receiving socket
        self.r = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        #create the histogram socket
        self.h = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        self.s.connect((self.HOST,self.SENDPORT))
        self.r.bind(('',self.RECVPORT))
        self.h.bind(('',self.HISTPORT))
        self.s.settimeout(0.1)        
        self.r.settimeout(0.1)
        self.h.settimeout(0.1)
        self.running = True
        self.receiveID = 100
        self.loggedIn=False
        self.login()

    def __del__(self):
        """Destructor that kills any active connection"""
        if self.loggedIn:
            self.close()

    def close(self):
        """Disconnect from the server"""
        if self.loggedIn:
            self.logout()
        self.r.close()
        self.s.close()
        self.h.close()
        self.running = False

    def packetHeader(self,commandID,data,a=0,b=0,c=0):
        """Create a packet header with three arbitrary parameters"""
        totalBytes = 4*6+len(data) #Assuming that there is no actual data
        self.receiveID += 1
        return struct.pack('iiiiii',self.receiveID,commandID,totalBytes,a,b,c)

    def getResp(self,count=1024):
        """Unpack a response from the server"""
        response, _ = self.r.recvfrom(count)
        receiveID,_,bcount,a,b,c=struct.unpack('iiiiii',response[:24])
        return (a,b,c,response[24:])

    def login(self):
        """Sign in to the server"""
        print("Logging In")
        self.s.send(self.packetHeader(self.LOGIN,b'\0python\0'))
        self.loggedIn = True
#        return self.getResp()

    def logout(self):
        """Sign out from the server"""
        print("Logging Out")        
        self.s.send(self.packetHeader(self.LOGOUT,b''))
        self.loggedIn = False
        return self.getResp()

    def startrun(self,runnumber):
        """Start collecting monitor data"""
        print("Starting Run")
        self.runnumber = runnumber
        self.s.send(self.packetHeader(self.STARTALL,b'',runnumber))
        self.running = True
        #return self.getResp()

    def stoprun(self):
        """Stop collecting monitor data"""
        print("Stopping Run")
        self.s.send(self.packetHeader(self.STOPALL,b''))
        self.running = False
        #return self.getResp()

    def save(self):
        """Save the data at the server."""
        print("Saving Data")
        self.s.send(self.packetHeader(self.SAVEDATA,b''))
        #return self.getResp()

    def getHistoData(self,monitor=0):
        """Get the TOF data from the monitor"""
        print("Getting Histogram Data")
        self.s.send(self.packetHeader(self.GETBMHISTODATA,b'',monitor))
        response,_ = self.h.recvfrom(4096)
#        response,_ = self.h.recvfrom(400,1)        
        (logtofres,tofres,bankindex,mintime,
         maxtime,datastarttime,logtof,numbins)=struct.unpack(self.MONTOF,response[:36])
        hist = np.frombuffer(response[36:],dtype=np.int32)
        return hist

    def getCount(self):
        """Returns the number of neutrons that have hit the monitor"""
        hist = self.getHistoData()
        return np.sum(hist[1:])

    def localSave(self,stream,time=0):
        """Creates a TOF histogram data file in the file stream"""
        hist = self.getHistoData()
        stream.write("File Saved for Run Number %d.\n" % self.runnumber)
        stream.write("This run had %d counts " % np.sum(hist[1:]))
        stream.write("and lasted %d milliseconds\n" % time)
        stream.write("User Name=Unkown, Proposal Number=Unknown\n")
        for i in range(1,len(hist)):
            stream.write("%d\t%d\n"%(i,hist[i]))
        
#if __name__ == "__main__":
#    d = Monitor()
#    try:
#        with open("1192mon.dat","w") as stream:
#            d.localSave(stream)
#    finally:
#        d.close()
##
##try:
##    print("login")
##    print("%d bytes sent" % (s.send(login(1000))))
##    print(r.recvfrom(1024))
##    print("starting")
##    print("%d bytes sent" % (s.send(startRun(1100,2000))))
##    sleep(5)
##    print("stoping")
##    print("%d bytes sent" % (s.send(stopRun(1100))))
##    sleep(5)
##    print("saving")
##    print("%d bytes sent" % (s.send(save(1100))))
##    sleep(5)
##    print("logout")
##    print("%d bytes sent" % (s.send(logout(1200))))
##    print s
##    s.close()
##except socket.error,msg:
##    s.close()
##    print msg

##
##m=Monitor()
##m.startrun(9876)
##m.stoprun()
##temp=m.getHistoData()

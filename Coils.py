"""This module handles controlling the current through the solenoids

This code was written to talk with a custom labview server on the
current control computer.  Note that, currently, the server does
not respond with the current currents.  When you first load the
module, you should set all of the current values to synchronize
with the server.

"""

import __future__
import socket
import struct
from time import sleep

class Coils:
    """This object manages the connection to the current control server"""
    HOST = "192.168.70.160"#IP address for the server
    PORT=7892#port number for the server

    def __init__(self):
        """Creates the connection object"""
        self.currents = [0 for i in range(12)]

    def set(self,cur,val):
        """Sets that value for one of the power supplies"""
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
        s.connect((self.HOST,self.PORT))
        
        self.currents[cur]=val
        temp=struct.pack('>Bd',cur,val)
        try:

            s.send(temp)
            result = s.recv(9)
            print result==temp
            print("Closing")
            s.close()
#            return result
            return 0
        except socket.error,err:
            print(err)
            s.close()

    def triangle(self,tri,val):
        """Sets the current for a given triangle"""
        self.set(tri-1,val)
    def getTriangle(self,tri):
        """Returns the value of the current in the slected triangle"""
        return self.currents[tri-1]

    def sample(self,val):
        """Sets the current in the sample area"""
        self.set(8,val)
    def getSample(self):
        """Returns the value of the current in the sample environment coil"""
        return self.currents[8]
    def guides(self,val):
        """Sets the current in the guide"""
        self.set(9,val)
    def getGuides(self):
        """Returns the value of the current in the guide field coils"""
        return self.currents[9]
    def flipper(self,val):
        """Sets the current in the flipping coil"""
        self.set(10,val)
    def flip(self):
        """Reverses the current through the flipping coil"""
        self.set(10,-1*self.currents[10])
    def getFlipper(self):
        """Returns the value of the current in the flipping coil"""
        return self.currents[10]
    def phase(self,val):
        """Sets the current in the phase coil"""
        self.set(11,val)
    def getPhase(self):
        """Returns the value of the current in the phase coil"""
        return self.currents[11]


if __name__=="__main__":
    coils = Coils()
    for i in range(4):
        coils.set(i,0)
    

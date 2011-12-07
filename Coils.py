"""This module handles controlling the current through the solenoids

This code was written to talk with a custom labview server on the
current control computer.  Note that, currently, the server does
not respond with the current currents.  When you first load the
module, you should set all of the current values to synchronize
with the server.

"""

import __future__
import xmlrpclib

class Coils(xmlrpclib.ServerProxy):
    """This object manages the connection to the current control server"""
    HOST = "http://192.168.70.160"#IP address for the server
    PORT=7892#port number for the server

    def __init__(self):
        """Creates the connection object"""
        xmlrpclib.ServerProxy.__init__(self,self.HOST + ":" + str(self.PORT) + "/RPC2")

    def flip(self):
        """Reverses the current through the flipping coil"""
        self.proxy.flipper(-1*self.proxy.getFlipper())


if __name__=="__main__":
    coils = Coils()
    for i in range(1,5):
        coils.triangle(i,i*2-1)
    

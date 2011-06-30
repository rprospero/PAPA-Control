"""This module contains code for spawning a new process for the detector.

DetectorProcess creates a new process that runs in an infinite loop.  That
process can be sent commands via the DetectorProcess object.  In reality,
this should be refactored out into a completely separate server process,
as opposed to a mere child process, but that will have to wait for ver. 2.0

"""

import multiprocessing
from Detector import Detector
from time import sleep

#Signals for the Detector Thunk
QUIT = 0
START = 10
STOP = 20
PAUSE = 30
RESUME = 40
RUNNUMBER = 100
DIRECTORY = 200
N_COUNT = 300
PARAM = 900
QUERY = 910


def DetectorThunk(conn,dir='C:/PAPA Control/',datacount=1000):
    """An infinite loop for controlling the detector

    Keyword arguments:
    conn -- a connection stream for communicating with the main process
    dir -- the directory in which to save data
    datacount -- the number of data points to attempts to read at a time

    The function loops through, either sleeping or recording data.  It polls
    its communication stream and expects a two element tuple.  The first
    element is an event code and the second is a tuple with the arguments for
    the event.

    """
    det = Detector() #detector object
    running = False
    paused = False
    runnumber = -1
    stream = None
    count = 0
    while True:
        if (not running) and (not conn.poll()):
            sleep(0.01)
            continue
        if conn.poll():
            cmd,args=conn.recv()
            if cmd==QUIT:
                break
            elif cmd==START:
                if runnumber<=0:
                    print("Error: Invalid Run #")
                    continue
                if not running:
                    stream = open(dir+("%04d"%runnumber)+'.pel','wb')
                    stream.write(det.makeHeader())
                    det.start()
                    running = True
                    count=0
            elif cmd==STOP:
                if running:
                    det.stop()
                    det.clear()
                    running = False
                    stream.close()
                    stream=None
                    continue
            elif cmd==PAUSE:
                print("Pausing Detector")
                det.stop()#Do NOT clear
                running = False
                paused = True
            elif cmd==RESUME:
                if paused:
                    print("Resuming")
                    det.start()
                    running = True
                else:
                    print("Cannot resume: detector not paused")
            elif cmd==RUNNUMBER:
                runnumber = args[0]
                conn.send("Run # set to %d"%runnumber)
            elif cmd==DIRECTORY:
                dir = args[0]
            elif cmd == N_COUNT:
                conn.send(count/2)#Correction Needed for 64 Bit Mode
            elif cmd==PARAM:
                opt,val=args
                det.setParam(opt,val)
            elif cmd == QUERY:
                conn.send(det.status[args[0]])
                #print det.status[args[0]]

            else:
                print("Did not recognize command %d"%cmd)
        if running:
            if stream is None: continue
            try:
                #Get the number of data points and the data
                #note that num is the number of 32 bit data
                #points given by the detector, which may or
                #may not be the actual  number of neutrons,
                #depending on  if the  detector is in 32 or
                #64 bit mode
                (num,data)=det.read(datacount)
            except RuntimeError,(err):
                print(err)
                break
            count += num
            #Pull only the actual data from the buffer
            if num < datacount:
                data=data[:num]
            stream.write(data.tostring())
            if num < datacount:
                stream.flush()
                sleep(0.01)
    del det
    print("Detector Process Halted!")
    return
    

class DetectorProcess:
    """An object to manage a child process that controls the detector."""
    def __init__(self):
        """Create a new detector process object and spawn a new process."""
        parent_conn,child_conn = multiprocessing.Pipe()
        #process object
        self.p=multiprocessing.Process(target=DetectorThunk,args=(child_conn,))
        self.p.start()
        #communication stream
        self.conn=parent_conn

    def __del__(self):
        """Process desutrctor"""
        self.quit()

    def send(self,x):
        """Send a message to the process"""
        self.conn.send(x)

    def recv(self):
        """Receive a message from the process"""
        return self.conn.recv()

    def quit(self):
        """Tell the process to end"""
        self.send((QUIT,()))
    def start(self):
        """Tell the process to start recording"""
        self.send((START,()))
    def stop(self):
        """Tell the process to stop recording"""
        self.send((STOP,()))
    def runnumber(self,num):
        """Update the number of the current run"""
        self.send((RUNNUMBER,(num,)))
        return self.recv()
    def directory(self,dir):
        """Change the output directory"""
        self.send((DIRECTORY,(dir,)))
    def count(self):
        """Report the number of data points collected"""
        self.send((N_COUNT,()))
        return self.recv()
    def setParam(self,option,value):
        """Change one of the detector's settings"""
        self.send((PARAM,(option,value)))
    def query(self,option):
        """Change one of the detector's settings"""
        self.send((QUERY,(option,)))
        while not self.conn.poll():
            pass
        return self.conn.recv()

if __name__ == '__main__':
    dp = DetectorProcess()
    sleep(1)
    print(dp.runnumber(5))
    sleep(1)
    dp.start()
    sleep(30)
    dp.stop()

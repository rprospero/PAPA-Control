"""This application runs the SESAME instrument"""

import __future__
import Instrument
import Coils
import smtplib
from XMLManifest import XMLManifest
import multiprocessing
from time import sleep,clock,localtime,asctime
import reader
import numpy as np

#Signals for the control process
QUIT=0
START=10
STOP=20
FLIPPER=100
PHASE=110
GUIDES=120
SAMPLE=130
TRIANGLE=140
SET_PARAM=200
QUERY=210
SET_COMMAND=300
SET_ONES=310

import logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                    datefmt="%m-%d %H:%M",
                    filename="C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/controllog.txt",
                    filemode="a")
console = logging.StreamHandler()#for writing to console
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")#The console just needs the message
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

def mailmessage(subject,message,password):
    fromaddress="Sesame.Beamline@gmail.com"
    toaddresses=["Sesame.Beamline@gmail.com","adlwashi@indiana.edu",
                 "pstonaha@indiana.edu","gtwarren@indiana.edu"]#,"helkaise@indiana.edu",
#                 "8123205472@vtext.com"]
    logging.info("Sending e-mail: %s",message)
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com",465)
        server.login(fromaddress,password)
        server.sendmail(fromaddress,
                        toaddresses,
                        "FROM:\"SESAME Beamline\" <"+fromaddress+">\n"
                        +"TO: "+",".join(toaddresses)+"\n"
                        +"SUBJECT:"+subject+"\n\n"+message)
        server.quit()
    except smtplib.SMTPException:
        logging.error("Failed to connect to mail server",exc_info=true)

def ones(i,coils,ratio):
    while True: yield 1

def flip(i,coils,ratio):
    (n,d)=ratio
    while True:
        yield n
        coils.guides(-1*coils.getGuides())        
        (n,d)=(d,n)

def triple(i,coils,ratio):
    (bsfa,bfsfa,bsa)=ratio
    coils.flipper(7)
    while True:
            coils.guides(7)
            coils.phase(7)
            yield bsfa
            coils.guides(7)
            coils.phase(-7)
            yield bfsfa
            coils.guides(-7)
            coils.phase(7)
            yield bsa

def flipperefficiency(i,coils,ratio):
    #5/5/2010 the following supplies control the following flippers
    #Guides Negative -> Flipper 1 Rear Field Up
    #Flippers Negative -> Flipper 2 Front Field Down
    #Phase Negative -> Static Flipper Fields Down
    (uu,ud,du,dd) = ratio
    coils.phase(7)
    while True:
        coils.flipper(7)
        coils.guides(7)
        yield uu
        coils.flipper(-7)
        coils.guides(7)
        yield ud
        coils.flipper(7)
        coils.guides(-7)
        yield du
        coils.flipper(-7)
        coils.guides(-7)
        yield dd

def currentscan(i,coils,ratio):
    (n,d)=ratio
    while True:
        for cur in [2.0 + x/20.0 for x in range(61)]:
#            for i in range(1,5):
#            coils.triangle(8,cur)
            coils.phase(cur)
            yield n
#            coils.flipper(-1*coils.getFlipper())
            coils.sample(-1*coils.getSample())
            yield d
#            coils.flipper(-1*coils.getFlipper())
            coils.sample(-1*coils.getSample())

def gainscan(i,coils,ratio):
    xgains = [320,415,357,375,568,412,447,530,650,0]
    ygains = [550,377,415,345,365,490,407,352,430,505]
    while True:
        for (n,x,y) in zip(range(10),xgains,ygains):
            logging.info('Setting X%d and Y%d to ten',n,n)
            i.setParam('gain for X',(n,10))
            i.setParam('gain for Y',(n,10))
            logging.debug("Yielded")
            yield 30
            logging.info('Restoring X%d and Y%d from ten',n,n)
            i.setParam('gain for X',(n,x))
            i.setParam('gain for Y',(n,y))



def thresholdscan(i,coils,ratio):
    logging.debug("Starting scan")
    t = 10
    while True:
        logging.info("Thresold: %i",t)
        i.setParam('trigger thresholds for papa strobe',(t,1023))
        for gain in range(20):
            logging.info("Gain: %i", (gain*20+455))
            i.setParam('gain for strobe pmt',gain*20+455)
            yield 3
        t += 10

def findMin(x,ylow,ycen,yhigh,h):
    logging.debug( "findMin")
    return (4*x*ycen-(h+2*x)*ylow+(h-2*x)*yhigh)/(4*ycen-2*(ylow+yhigh))

def readLatest(i):
    logging.debug( "Read Latest")
    path = i.getPath()+("%04d"%i.subrun)+".pel"
    logging.debug( path)
    p = reader.PelFile(path)
    data = np.sum(p.make3d(),axis=2) #make 2D map
    return np.std(data)

def base(i,coils,ratio):
    gains = ["gain for X"+str(x) for x in range(9)]
    gains.extend(["gain for Y"+str(x) for x in range(9)])
    dict = {}
    for gain in gains:
        dict[gain] = i.query(gain)
    while True:
        for gain in gains:
            init = dict[gain]
            for x in range(init-200,init+201,100):
                logging.info( gain)
                logging.info( x)
                i.setParam(gain[:-1],(int(gain[-1]),x))
                yield 7
                i.setParam(gain[:-1],(int(gain[-1]),init))


def dumper(i,coils,ratio):
    adcs = [[None,('gain for X',9),('gain for Y',9)],
         [('gain for X',8),('gain for X',7),('gain for Y',7)],
         [('gain for Y',8),('gain for X',6),('gain for Y',6)],
         [('gain for X',5),('gain for X',4),('gain for Y',4)],
         [('gain for Y',5),('gain for X',3),('gain for Y',3)],
         [('gain for X',2),('gain for X',1),('gain for Y',1)],
         [('gain for X',2),('gain for X',0),('gain for Y',0)]]
    for am in range(7):
        ins.setParam('mode',am)
        base = [None,None,None]
        #record intial values
        logging.info("Record initial values")
        for i in range(3):
            if adcs[am][i] is not None:
                logging.debug( adcs[am][i])
                logging.debug( adcs[am][i][0]+str(adcs[am][i][1]))
                base[i] = ins.query(adcs[am][i][0]+str(adcs[am][i][1]))
        #scan the gain
        logging.info("Scan the gain")
        for gain in range(100,800,100):
            for adc in adcs[am]:
                if adc is not None:
                    ins.setParam(adc[0],(adc[1],gain))
            yield 6.0/120.0
            sleep(5)
        #return to initial value
        for i in range(3):
            if adc is not None:
                ins.setParam(adc[0],(adc[1],gain))
    #We're finished, so just take a two year measurement
    ins.setParam('mode',14)
    yield 525600

def tune(i,coils,ratio):
    gains = ["gain for X"+str(x) for x in range(9)]
    gains.extend(["gain for Y"+str(x) for x in range(9)])
    dict = {}

    h=100
    while True:
        for gain in gains:
            base = i.query(gain)
            logging.info( "Testing " + gain + " at " + str(base))
            yield 2
            ycen = readLatest(i)
            logging.info( "Std:\t%f"%ycen)
            logging.info( "Testing " + gain + " at " + str(base-h))
            i.setParam(gain[:-1],(int(gain[-1]),base-h))
            yield 2
            ylow = readLatest(i)
            logging.info( "Std:\t%f"%ylow)
            logging.info( "Testing " + gain + " at " + str(base+h))
            i.setParam(gain[:-1],(int(gain[-1]),base+h))
            yield 2
            yhigh = readLatest(i)
            logging.info( "Std:\t%f"%yhigh)
            logging.info( "Set Complete")
            newbase = int(findMin(base,ylow,ycen,yhigh,h))
            newbase = min(900,max(100,newbase))
            logging.info( "The new " + gain + " is " + str(newbase))
            i.setParam(gain[:-1],(int(gain[-1]),newbase))
        if h > 25:
            h = h/2
            

def controlThunk(conn,steptime=120):
    """An infinite loop that controls the insturment and coils"""
    i = Instrument.Instrument()
    password = i.getPassword()
    beamon = True
    coils = Coils.Coils()
    running = False
    flipping = False
    count = 0
    starttime = 0
    command = ones
    generator = command(i,coils,(1,1))
    n = generator.next()
    logging.debug("Starting Main Loop")
    while True:
        if (not running) and (not conn.poll()):
            sleep(0.01)
            continue
        if conn.poll():
            cmd,args=conn.recv()
            if cmd==QUIT:
                if running:
                    i.stop()
                break
            if cmd==START:
                generator = command(i,coils,args[0])
                n = generator.next()
                i.updateRunnumber()
                manifest = XMLManifest(i.getPath()+"Manifest.xml",
                                       i.getRunnumber())
                i.start()
                starttime = clock()
                ltime = asctime(localtime())
                running = True
            if cmd==STOP:
                (time,monitor_count,detector_count) = i.stop()
                mp = {"subrun":i.subrun} #Manifest Parameters
                mp["time"]=time
                mp["start"]=ltime
                mp["monitor count"]=monitor_count
                mp["monitor file"]=i.getLocalMonitorFile()
                mp["detector count"]=detector_count
                mp["detector file"]=i.getLocalMonitorFile()[:-7]+".pel"
                mp["flipping current"]=coils.getFlipper()
                mp["phase current"]=coils.getPhase()
                mp["guide current"]=coils.getGuides()
                mp["sample current"]=coils.getSample()
                for tri in range(1,9):
                    mp["triangle %d"%tri]=coils.getTriangle(tri)
                manifest.addRun(mp)
                running = False
            if cmd==FLIPPER: coils.flipper(args[0])
            if cmd==GUIDES: coils.guides(args[0])
            if cmd==PHASE: coils.phase(args[0])
            if cmd==SAMPLE: coils.sample(args[0])
            if cmd==TRIANGLE: coils.triangle(args[0],args[1])
            if cmd==SET_PARAM:
                if running:
                    logging.warning("Cannot adjust detector paramters while the instrument is running")
                else:
                    i.setParam(args[0],args[1])
            if cmd==QUERY:
                conn.send(i.query(args[0]))
            if cmd==SET_COMMAND:
                command = args[0]
        if running:
            #if we've run long enough, start a new sub-run
            if clock()-starttime > steptime*n:
                logging.debug("Stopping Instrument")
                (time,monitor_count,detector_count) = i.stop()
                mp = {"subrun":i.subrun} #Manifest Parameters
                mp["time"]=time
                mp["start"]=ltime
                mp["monitor count"]=monitor_count
                mp["monitor file"]=i.getLocalMonitorFile()
                mp["detector count"]=detector_count
                mp["detector file"]=i.getLocalMonitorFile()[:-7]+".pel"
                mp["flipping current"]=coils.getFlipper()
                mp["phase current"]=coils.getPhase()
                mp["guide current"]=coils.getGuides()
                mp["sample current"]=coils.getSample()
                logging.debug("E-mail time")
                if beamon and monitor_count/time < 2.0:
                    mailmessage("LENS is down","I am not recieving many neutrons.  Is the beam off?",password)
                    beamon=False
                elif not beamon and monitor_count/time > 2.0:
                    mailmessage("LENS is up","I am recieving neutrons again.",password)
                    beamon=True    
                for tri in range(1,9):
                    mp["triangle %d"%tri]=coils.getTriangle(tri)
                logging.debug("Update Manifest")
                manifest.addRun(mp)
                ltime = asctime(localtime())
                starttime = clock()
                n=generator.next()
                logging.debug("Starting Instrument")
                i.start()
    del i

class Control:
    """This object maintains a Control Process for running the instrument"""
    def __init__(self):
        """Create a control object"""
        parent_conn,child_conn = multiprocessing.Pipe()
        self.p=multiprocessing.Process(target=controlThunk,
                                       args=(child_conn,120))
        self.p.start()
        self.conn=parent_conn

    def __del__(self):
        """Shuts down the control process when the object is destroyed"""
        self.conn.send((QUIT,()))

    def start(self,ratio=(1,1)):
        """Begins collecting data
        
        Keyword arguments:
        flipping -- should the flipper flip between subruns?
        ratio -- a tuple containing the ratio of positive 
                 to negative flipper current

        Note that, when flipping is performed, the first state is
        always the positive current.

        """
        self.conn.send((START,(ratio,)))


    def setCommand(self,command):
        self.conn.send((SET_COMMAND,(command,)))

    def flippingrun(self):
        """Begins collecting data with flipping between subruns.

        Keyword arguments:
        ratio -- a tuple containing the ratio of positive 
                 to negative flipper current

        """
        self.setCommand(flip)
    def triplerun(self):
        """Begins collecting three of the four spin states for checking
        the efficiency of the bender, supermirror, and analyzer.

        ratio -- the relative lengths of time to measure bsfa,bsa,and bfsfa
        
        """
        self.setCommand(triple)
    def quadrun(self):
        """Begins collecting all four flipping states for checking the
        flipper efficiency

        ratio -- the relative lengths of time to measure up-up, up-down,
                down-up, and down-down
        
        """
        self.setCommand(flipperefficiency)
    def curscan(self):
        """Performed a flipping run over a range of triangle currents

        ratio -- Scan through current on triangle pair one in both directions,
        using a 0.01 offset to mark the two different hysteresis states.
        
        """
        self.setCommand(currentscan)
    def threshscan(self):
        self.setCommand(makeThresholdScan)

    def tune(self):
        self.setCommand(makeDumper)

    def gainscan(self):
        self.setCommand(makeGainScan)
        
    def stop(self):
        """Ends data collection"""
        self.conn.send((STOP,()))

    def flipper(self,val):
        """Set the current in the fliping solenoid"""
        self.conn.send((FLIPPER,(val,)))
    def phase(self,val):
        """Set the current in the phase coils"""
        self.conn.send((PHASE,(val,)))
    def guides(self,val):
        """Set the current in the guid fields"""
        self.conn.send((GUIDES,(val,)))
    def sample(self,val):
        """Set the current in the sample area"""
        self.conn.send((SAMPLE,(val,)))
    def triangle(self,tri,val):
        """Set the current in the chosen triangle"""
        self.conn.send((TRIANGLE,(tri,val)))

    def detectorParameter(self,parameter,val):
        """Set one of the status variables in the detector"""
        self.conn.send((SET_PARAM,(parameter,val)))
    def query(self,parameter):
        """Prints out the value of the chosen status variable on the detector"""
        self.conn.send((QUERY,(parameter,)))
        while not self.conn.poll():
            sleep(0.01)
        return self.conn.recv()

    def allOn(self):
        """Turn on all of the power supplies to a default value"""
        self.flipper(5)
        self.phase(5)
        self.guides(5)
        self.sample(5)
        for i in range(1,9):
            self.triangle(i,5)

    def allOff(self):
        """Kill the current in all of the power supplies"""
        self.flipper(0)
        self.phase(0)
        self.guides(0)
        self.sample(0)
        for i in range(1,9):
            self.triangle(i,0)

def exit():
    global c
    global d
    global q
    del(c)
    del(d)
    del(q)
    quit()

if __name__ == "__main__":
    c=Control()
    d=c.detectorParameter
    q=c.query
#    c.allOn()

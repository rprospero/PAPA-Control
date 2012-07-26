"""This application runs the SESAME instrument"""

import __future__
import Instrument
import Coils
import smtplib
from XMLManifest import XMLManifest
import json
import multiprocessing
from time import sleep,clock,localtime,asctime
import reader
import numpy as np
import sys

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
console = logging.StreamHandler(sys.stdout)#for writing to console
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")#The console just needs the message
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

def mailmessage(subject,message,password):
    logging.info("Loading e-mail parameters:")
    mail = {}
    with open("C:/PAPA Control/trunk/mail.json","r") as jfile:
        mail = json.load(jfile)
    toaddress = mail['toaddresses']
    fromaddress = mail['fromaddress']
    password = mail['password']
    logging.debug("Sending e-mail: %s",message)
    logging.debug("E-mail sender: %s",fromaddress)
    logging.debug("E-mail sender: %s",str(toaddress))
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com",465)
        logging.debug("Established smtp connection")
        server.login(fromaddress,password)
        logging.debug("Logged into mail server")
        server.sendmail(fromaddress,
                        toaddress,
                        "FROM:\"SESAME Beamline\" <"+fromaddress+">\n"
                        +"TO: "+",".join(toaddress)+"\n"
                        +"SUBJECT:"+subject+"\n\n"+message)
        logging.debug("Mail sent")
        server.quit()
    except smtplib.SMTPException:
        logging.error("Failed to connect to mail server",exc_info=true)
    except smtplib.SMTPHeloError:
        logging.error("No Helo from server",exc_info=true)
    except smtplib.SMTPAuthenticationError:
        logging.error("Invalid username and password",exc_info=true)
    except smtplib.SMTPException:
        logging.error("No authentication method available",exc_info=true)
    except Exception as e:
        logging.error("Unknown exception: %s"%str(type(e)))
        logging.error("Exception arguments: %s"%str(e.args))
        logging.error("Exception: %s"%str(e))

def ones(i,coils,ratio):
    while True: yield 1

def flip(i,coils,ratio):
    (n,d)=ratio
    setter = coils.flipper
    getter = coils.getFlipper()
    setter(abs(getter()))
    while True:
        yield n
        setter(-1*getter())
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
    s = abs(coils.getSample())
    p = abs(coils.getPhase())
    logging.debug("Acquired default currents for efficiency run.")
    logging.debug("s = %s"%(str(s)))
    logging.debug("p = %s"%(str(p)))
    while True:
        coils.sample(s)
        coils.phase(p)
        logging.debug("Yielding flipper efficiency state")
        yield uu
        coils.sample(-s)
        coils.phase(p)
        yield ud
        coils.sample(s)
        coils.phase(-p)
        yield du
        coils.sample(-s)
        coils.phase(-p)
        yield dd

def currentscan(i,coils,ratio):
    """
    Runs a current scan on the guides slipper while flipping on the
    sample flipper.  This function is designed as a command for the
    control object.


    i = instrument object
    coils = coils object
    ratio = a tuple of form:

    ((n,d),currents) where
    n = number of two minute units to spend in the up state
    d = number of two minute units to spend in the down state
    currents = a list of currents to try on the guides supply.
    """

    logging.debug(ratio)
    (temp,currents)=ratio
    logging.debug(currents)
    (n,d) = temp
    logging.debug(n)
    logging.debug(str(coils))
    logging.debug(coils.getFlipper())
    logging.debug(coils.getPhase())
    logging.debug("Initialized flipper coil")
    while True:
        for cur in currents:
            logging.info("Current " + str(cur))
            coils.phase(float(cur))
            logging.debug("Yield n: " + str(n))
            yield n
            coils.flipper(-1*coils.getFlipper())
            yield d
            coils.flipper(-1*coils.getFlipper())

def alphascan(i,coils,ratio):
    """
    Runs a current scan on the triangle currents while flipping on the
    sample flipper.  This function is designed as a command for the
    control object.


    i = instrument object
    coils = coils object
    ratio = a tuple of form:

    ((n,d),currents) where
    n = number of two minute units to spend in the up state
    d = number of two minute units to spend in the down state
    currents = a list of currents to try on the guides supply.
    """

    logging.debug(ratio)
    (temp,currents)=ratio
    logging.debug(currents)
    (n,d) = temp
    logging.debug(n)
    logging.debug(str(coils))
    logging.debug(coils.getFlipper())
    logging.debug(coils.getFlipper())
    logging.debug(abs(coils.getFlipper()))
    coils.flipper(abs(coils.getFlipper()))
    logging.debug("Initialized flipper coil")
    while True:
        for cur in currents:
            logging.debug("Current " + str(cur))
            [coils.triangle(i,cur) for i in range(1,5)]
            logging.debug("Yield n" + str(n))
            yield n
            coils.flipper(-1*coils.getFlipper())
            yield d
            coils.flipper(-1*coils.getFlipper())





def gainscan(i,coils,ratio):
    xgains = [320,415,357,375,568,300,250,200,450,0]
    ygains = [720,377,415,545,365,490,407,175,190,505]
    while True:
        for (n,x,y) in zip(range(10),xgains,ygains):
            logging.info('Setting X%d and Y%d to ten',n,n)
            i.setParam('gain for X',(n,10))
            i.setParam('gain for Y',(n,10))
            logging.debug("Yielded")
            yield 2
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
            for x in range(init-100,init+150,50):
                logging.info( gain)
                logging.info( x)
                i.setParam(gain[:-1],(int(gain[-1]),x))
                yield 2
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
                if running:
                    logging.warning("Please stop the current run before starting the next run.")
                else:
                    logging.debug("Creating generator")
                    generator = command(i,coils,args[0])
                    logging.debug("Starting generator")
                    n = generator.next()
                    i.updateRunnumber()
                    manifest = XMLManifest(i.getPath()+"Manifest.xml",
                                           i.getRunnumber())
                    i.start()
                    starttime = clock()
                    ltime = asctime(localtime())
                    logging.debug("Starting running")
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
        logging.debug("Creating Control object")
        parent_conn,child_conn = multiprocessing.Pipe()
        self.p=multiprocessing.Process(target=controlThunk,
                                       args=(child_conn,120))
        logging.debug("Starting multiprocessing")
        self.p.start()
        self.conn=parent_conn

    def __del__(self):
        """Shuts down the control process when the object is destroyed"""
        logging.debug("Killing Control Object")
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
        logging.debug("Starting Run")
        self.conn.send((START,(ratio,)))


    def setCommand(self,command):
        logging.debug("Setting command")
        self.conn.send((SET_COMMAND,(command,)))

    def flippingrun(self,ps="flipper"):
        """Begins collecting data with flipping between subruns.

        Keyword arguments: ps -- A string containing the name of the
        power supply which needs to be flipped.  Acceptible values are
        "flipper", "guides", "phase", and "sample".

        """
        logging.debug("Selecting Flipping Run")
        self.setCommand(flip)
    def triplerun(self):
        """Begins collecting three of the four spin states for checking
        the efficiency of the bender, supermirror, and analyzer.

        ratio -- the relative lengths of time to measure bsfa,bsa,and bfsfa
        
        """
        logging.debug("Triple Run")
        self.setCommand(triple)
    def quadrun(self):
        """Begins collecting all four flipping states for checking the
        flipper efficiency

        ratio -- the relative lengths of time to measure up-up, up-down,
                down-up, and down-down
        
        """
        logging.debug("Quad Run")
        self.setCommand(flipperefficiency)
    def curscan(self):
        """Performed a flipping run over a range of phase currents

        currents: list of current values to test on the phase coil
        """
        logging.debug("Current Scan")
        self.setCommand(currentscan)

    def ones(self):
        """Set the instrument to run in a single flipper state"""
        logging.debug("Single State Measurement")
        self.setCommand(ones)

    def threshscan(self):
        """Run a threshold scan on the detector PMTs"""
        logging.debug("Threshold Scan")
        self.setCommand(makeThresholdScan)

    def tune(self):
        """Attempt to tune the PMTs in the detector"""
        logging.debug("Detector Tune")
        self.setCommand(makeDumper)

    def gainscan(self):
        """Scan the gains for the PMTs"""
        logging.debug("Gain Scan")
        self.setCommand(makeGainScan)
        
    def stop(self):
        """Ends data collection"""
        logging.debug("Stopping Detector")
        self.conn.send((STOP,()))

    def flipper(self,val):
        """Set the current in the fliping solenoid"""
        logging.debug("Setting Flipper to %f",val)
        self.conn.send((FLIPPER,(val,)))
    def phase(self,val):
        """Set the current in the phase coils"""
        logging.debug("Setting phase to %f",val)
        self.conn.send((PHASE,(val,)))
    def guides(self,val):
        """Set the current in the guid fields"""
        logging.debug("Setting guides to %f",val)
        self.conn.send((GUIDES,(val,)))
    def sample(self,val):
        """Set the current in the sample area"""
        logging.debug("Setting sample to %f",val)
        self.conn.send((SAMPLE,(val,)))
    def triangle(self,tri,val):
        """Set the current in the chosen triangle"""
        logging.debug("Setting triangle %i to %f",tri,val)
        self.conn.send((TRIANGLE,(tri,val)))

    def detectorParameter(self,parameter,val):
        """Set one of the status variables in the detector"""
        logging.debug("Setting parameter %s to %s",parameter,str(val))
        self.conn.send((SET_PARAM,(parameter,val)))
    def query(self,parameter):
        """Prints out the value of the chosen status variable on the detector"""
        logging.debug("Requesting parameter %s",parameter)
        self.conn.send((QUERY,(parameter,)))
        while not self.conn.poll():
            sleep(0.01)
        return self.conn.recv()

    def allOn(self,current=5):
        """Turn on all of the power supplies to a constant value.  The default is five amps."""
        logging.debug("Turning on all the power supplies.",str(current))
        self.flipper(current)
        self.phase(current)
        self.guides(current)
        self.sample(current)
        for i in range(1,9):
            self.triangle(i,current)

    def allOff(self):
        """Kill the current in all of the power supplies"""
        logging.debug("Turning off all the power supplies.")
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

"""This application runs the SESAME instrument"""

import __future__
import Instrument
import Coils
import smtplib
from XMLManifest import XMLManifest
import multiprocessing
from time import sleep,clock,localtime,asctime

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
SET_FLIPPING=320
SET_TRIPLE=330
SET_FLIPPER_EFFICIENCY=340
SET_CUR_SCAN=350
SET_THRESH_SCAN=360
SET_GAIN_SCAN=370

def mailmessage(subject,message,password):
    fromaddress="Sesame.Beamline@gmail.com"
    toaddresses=["Sesame.Beamline@gmail.com","adlwashi@indiana.edu",
                 "pstonaha@indiana.edu","helkaise@indiana.edu",
                 "8123205472@vtext.com"]
    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login(fromaddress,password)
    server.sendmail(fromaddress,
                    toaddresses,
                    "FROM:\"SESAME Beamline\" <"+fromaddress+">\n"
                    +"TO: "+",".join(toaddresses)+"\n"
                    +"SUBJECT:"+subject+"\n\n"+message)
    server.quit()

def ones(a=0,b=0):
    while True: yield 1

##def flip(ratio,coils):
##    coils.flipper(-1*abs(coils.getFlipper()))
##    coils.phase(-7)
##    (n,d)=ratio
##    while True:
##        coils.flip()
##        yield n
##        (n,d)=(d,n)

def flip(ratio,coils):
    (n,d)=ratio
    while True:
        #coils.flip()
        yield n
        coils.flipper(-1*coils.getFlipper())        
#        coils.flipper(-1*coils.getFlipper())
        (n,d)=(d,n)

def triple(ratio, coils):
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

def flipperefficiency(ratio,coils):
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

def currentscan(ratio,coils):
    (n,d)=ratio
    while True:
        for cur in [4 + x/20.0 for x in range(21)]:
            coils.phase(cur)
            yield n
            coils.flipper(-1*coils.getFlipper())
            yield d
            coils.flipper(-1*coils.getFlipper())

def makeGainScan(i):
    xgains = [320,415,357,375,568,412,447,530,650,0]
    ygains = [550,377,415,345,365,490,407,352,430,505]
    print "Making Gain Scan"
    def gainscan(ratio,coils):
        print("Starting Gain Scan")
        while True:
            for (n,x,y) in zip(range(10),xgains,ygains):
                print('Setting X%d and Y%d to ten'%(n,n))
                i.setParam('gain for X',(n,10))
                i.setParam('gain for Y',(n,10))
                print("Yielded")
                yield 30
                print('Restoring X%d and Y%d from ten'%(n,n))
                i.setParam('gain for X',(n,x))
                i.setParam('gain for Y',(n,y))
    return gainscan


def makeThresholdScan(i):
    def thresholdscan(ratio,coils):
        print("Starting scan")
        t = 30
        while True:
            print("Thresold: %i" % t)
            i.setParam('trigger thresholds',(t,1023))
            for gain in range(25):
                print("Gain: %i" % (gain*20+20))
                i.setParam('gain for energy pmt',gain*20+20)
                yield 1
            t += 15
    return thresholdscan


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
    generator = command()
    n = generator.next()
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
                generator = command(args[0],coils)
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
                    print("Cannot adjust detector paramters while the instrument is running")
                else:
                    i.setParam(args[0],args[1])
            if cmd==QUERY:
                i.query(args[0])
            if cmd==SET_COMMAND:
                commval = args[0]
                if commval == SET_TRIPLE:
                    command = triple
                elif commval == SET_FLIPPING:
                    command = flip
                elif commval == SET_FLIPPER_EFFICIENCY:
                    command = flipperefficiency
                elif commval == SET_CUR_SCAN:
                    command = currentscan
                elif commval == SET_THRESH_SCAN:
                    print("Threshscan")
                    command = makeThresholdScan(i)
                elif commval == SET_GAIN_SCAN:
                    command = makeGainScan(i)
                    print("Command Set")
                else:
                    command = ones
        if running:
            #if we've run long enough, start a new sub-run
            if clock()-starttime > steptime*n:
                print("DEBUG: Stopping Instrument")
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
                print("DEBUG: E-mail time")
                if beamon and monitor_count/time < 16.0:
                    mailmessage("LENS is down","I am not recieving many neutrons.  Is the beam off?",password)
                    beamon=False
                elif not beamon and monitor_count/time > 16.0:
                    mailmessage("LENS is up","I am recieving neutrons again.",password)
                    beamon=True    
                for tri in range(1,9):
                    mp["triangle %d"%tri]=coils.getTriangle(tri)
                print("Debug: Update Manifest")
                manifest.addRun(mp)
                ltime = asctime(localtime())
                starttime = clock()
                n=generator.next()
                print ("DEBUG: Starting Instrument")
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

    def start(self,command=SET_ONES,ratio=(1,1)):
        """Begins collecting data
        
        Keyword arguments:
        flipping -- should the flipper flip between subruns?
        ratio -- a tuple containing the ratio of positive 
                 to negative flipper current

        Note that, when flipping is performed, the first state is
        always the positive current.

        """
        self.conn.send((SET_COMMAND,(command,)))
        self.conn.send((START,(ratio,)))

    def flippingrun(self,ratio):
        """Begins collecting data with flipping between subruns.

        Keyword arguments:
        ratio -- a tuple containing the ratio of positive 
                 to negative flipper current

        """
        self.start(SET_FLIPPING,ratio)
    def triplerun(self,ratio):
        """Begins collecting three of the four spin states for checking
        the efficiency of the bender, supermirror, and analyzer.

        ratio -- the relative lengths of time to measure bsfa,bsa,and bfsfa
        
        """
        self.start(SET_TRIPLE,ratio)
    def quadrun(self,ratio):
        """Begins collecting all four flipping states for checking the
        flipper efficiency

        ratio -- the relative lengths of time to measure up-up, up-down,
                down-up, and down-down
        
        """
        self.start(SET_FLIPPER_EFFICIENCY,ratio)
    def curscan(self,ratio):
        """Performed a flipping run over a range of triangle currents

        ratio -- Scan through current on triangle pair one in both directions,
        using a 0.01 offset to mark the two different hysteresis states.
        
        """
        self.start(SET_CUR_SCAN,ratio)
    def threshscan(self):
        self.start(SET_THRESH_SCAN,(1,1))
    def gainscan(self):
        self.start(SET_GAIN_SCAN,(1,1))
        
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

    def allOn(self):
        """Turn on all of the power supplies to a default value"""
        self.flipper(7)
        self.phase(5)
        self.guides(5)
        self.sample(5)
        for i in range(1,9):
            self.triangle(i,10)

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
    from Combiner import combine
    c=Control()
    d=c.detectorParameter
    q=c.query
#    c.allOn()

import os
import os.path
import shutil
from optparse import OptionParser
import time

source = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data"
destination = "C:/Documents and Settings/sesaadmin/My Documents/Google Drive"

def sources(s):
    files = os.listdir(s)
    for file in files:
        yield os.path.join(s,file)

def directories(files):
    for file in files:
        if os.path.isdir(file):
            yield file

def numbered(min,files):
    for file in files:
        base = os.path.basename(file)
        if not base.isdigit():
            continue
        if int(base) >= min:
            yield file

def updated(dest,files):
    for file in files:
        backup = os.path.join(dest,os.path.basename(file))
        if not os.path.exists(backup):
            yield file
        elif os.path.getmtime(file) > os.path.getmtime(backup):
            yield file

def runs_to_update(min,path):
    for file in updated(destination,numbered(min,directories(sources(path)))):
        yield file

def copy_new_files(dest,directory):
    base = os.path.basename(directory)
    backup = os.path.join(dest,base)
    if not os.path.exists(backup):
        os.makedirs(backup)
    for file in updated(backup,sources(directory)):
        shutil.copyfile(file,os.path.join(backup,os.path.basename(file)))
        
def sync(src,dest,min):
    for i in runs_to_update(min,src):
        copy_new_files(dest,i)
        print i

if __name__=='__main__':
    usage = "%prof [options] minimum_run_number"
    parser = OptionParser()

    parser.add_option("--source",action="store",type="string",
                      default=source,help="Directory where the neutron data is stored.  Defaults to: %default")
    parser.add_option("--destination",action="store",type="string",
                      default=source,help="Directory where the neutron data is to be copied.  Defaults to: %default")
    parser.add_option("--rate",action="store",type="int",default=10,
                      help="How many minutes to sleep between syncs.  Defaults to %default")

    (options,min) = parser.parse_args()

    if len(min) != 1 or not min[0].isdigit():
        print("Error:  Need exactly one minimum run number to start.")
    else:
        while True:
            sync(options.source,options.destination,int(min[0]))
            time.sleep(60*options.rate)
    

from __future__ import print_function
from subprocess import call
from datetime  import datetime

def installIfNeeded(nameOnPip, notes="", log=print):
    from pkgutil import iter_modules

    # Check if the module is installed
    if nameOnPip not in [tuple_[1] for tuple_ in iter_modules()]:
        log("Installing " + nameOnPip + notes + " Library for Python")
        call(["sudo", "pip", "install", nameOnPip])
        
def log(message):
    print(datetime.now().strftime("%a %b %d %H:%M:%S") + " - " + str(message))        
    
# ADD LIST OF USED PACKAGE HERE
installIfNeeded("pycrypto", "For PWD Encryption (see /pwd)", log = log)    

# CREATE DEFAULT CAM_CALIB FILES
all_calibs = ['Day','Calibration','Night']
for cal_file in  all_calibs:
    f= open('./cam_calib/'+cal_file,"w+")
    f.write("Brightness=128\nContrast=128\nGamma=128")
    log(cal_file + " created")
    f.close() 
    
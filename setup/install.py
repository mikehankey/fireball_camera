from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path

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

# CREATE DEFAULT CAM_CALIB FILES IF THEY DON'T EXIST
all_calibs = ['Day','Calibration','Night']
for cal_file in  all_calibs:
    fname = './cam_calib/'+cal_file;
    if(os.path.isfile(fname)):
        log( cal_file + 'parameter file already exists (creation skipped)');
    else:
        f= open(fname,"w+")
        f.write("Brightness=128\nContrast=128\nGamma=128")
        log(cal_file + " created")
        f.close() 
       

# Install Dependencies for the App
subprocess.Popen(['sudo','npm', 'install','-g'],cwd=r'/home/pi/AMSCam')
log("Please, wait until NPM INSTALL is done")

subprocess.Popen(['bower', 'install'],cwd=r'/home/pi/AMSCam')
log("Please, wait until BOWER INSTALL is done")
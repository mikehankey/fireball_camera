from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path

#Log
def log(message):
    print(datetime.now().strftime("%a %b %d %H:%M:%S") + " - " + str(message))            

# Install Dependencies for the App
sp = subprocess.Popen(['sudo','npm', 'install','-g'],cwd=r'/home/pi/AMSCam')
log("NPM INSTALL is running")
sp.wait();
log("NPM INSTALL done")

sp = subprocess.Popen(['bower', 'install'],cwd=r'/home/pi/AMSCam')
log("BOWER INSTALL is running")
sp.wait();
log("BOWER INSTALL done")
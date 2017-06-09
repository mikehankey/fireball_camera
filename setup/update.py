from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path

def log(message):
    #return(datetime.now().strftime("%a %b %d %H:%M:%S") + " - " + str(message))        

# Git pull on the APP
sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/AMSCam')
log("App is updating - please wait.")
sp.wait();
log("APP Updated")

# Install Dependencies for the App
sp = subprocess.Popen(['sudo','npm', 'install','-g'],cwd=r'/home/pi/AMSCam')
log("NPM INSTALL is running")
sp.wait();
log("NPM INSTALL done")
 
# os.chdir('/home/pi/AMSCam')
sp = subprocess.Popen(['bower', 'install'],cwd=r'/home/pi/AMSCam')
log("BOWER INSTALL is running")
sp.wait();
log("BOWER INSTALL done")

# Stop the APP
sp = subprocess.Popen(['killall','node'])
log("App is shutting down")
sp.wait();
log("App shut down")

return "restart"

  
# WILL RESTART THANKS TO FOREVER
# Restart the App
#sp = subprocess.Popen(['node','app.js'],cwd=r'/home/pi/AMSCam', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#log("App running")
#sp.wait();
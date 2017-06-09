from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path

    

# Git pull on the APP
sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/AMSCam')
sp.wait();

# Install Dependencies for the App
sp = subprocess.Popen(['sudo','npm', 'install','-g'],cwd=r'/home/pi/AMSCam')
sp.wait();
 
# os.chdir('/home/pi/AMSCam')
sp = subprocess.Popen(['bower', 'install'],cwd=r'/home/pi/AMSCam')
sp.wait();

# Stop the APP
sp = subprocess.Popen(['forever','app.js'],cwd=r'/home/pi/AMSCam', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
sp = subprocess.Popen(['killall','forever'])
sp.wait();

print("Restarting")

  
# WILL RESTART THANKS TO FOREVER
# Restart the App
#sp = subprocess.Popen(['node','app.js'],cwd=r'/home/pi/AMSCam', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#log("App running")
#sp.wait();
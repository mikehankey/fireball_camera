from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path
import json

# Git pull on the Python
sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/fireball_camera')
sp.wait();  

# Git pull on the APP
sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/AMSCam')
sp.wait();

# Install Dependencies for the App
sp = subprocess.Popen(['sudo','npm', 'install','-g'],cwd=r'/home/pi/AMSCam')
sp.wait();
 
sp = subprocess.Popen(['bower', 'install'],cwd=r'/home/pi/AMSCam')
sp.wait();

# Update the Calib Files
all_calibs = ['Day','Calibration','Night']
for index,cal_file in enumerate(all_calibs):
    
    config = {}
    file = open("/home/pi/fireball_camera/cam_calib/"+cal_file, "r+")
    
    for line in file:
      line = line.strip('\n')
      #Find first index of =
      c = line.index('=')
      config[line[0:c]] = line[c+1:]
    
    try:
      config['Exposure']
    except:
      if (cal_file == 'Calibration'):
        file.write('Exposure=25\n')   
      else:
        file.write('Exposure=50\n')   
    file.close()    


# Stop the APP
sp = subprocess.Popen(['sudo','forever','app.js'],cwd=r'/home/pi/AMSCam', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
sp = subprocess.Popen(['killall','forever'])
sp.wait();

print("Restarting")
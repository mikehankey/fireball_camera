from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path
import json

def log(message):
    print( datetime.now().strftime("%a %b %d %H:%M:%S") + " - " + str(message)   )      

# Git pull on the Python
sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/fireball_camera')
sp.wait();  
log('fireball_camera updated');

# Git pull on the APP
sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/AMSCam')
sp.wait();
log('AMSCam updated');

# Install Dependencies for the App
sp = subprocess.Popen(['sudo','npm','install'],cwd=r'/home/pi/AMSCam')
sp.wait();
log('NPM modules OK');
 
sp = subprocess.Popen(['sudo', 'bower', 'install','--allow-root'],cwd=r'/home/pi/AMSCam')
sp.wait();
log('BOWER modules OK');

# Update the Calib Files (ADD EXPOSURE FOR THE FILES THAT DON'T HAVE IT YET)
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
 

log('Calibration files ok.');
 
# Restart the APP
sp = subprocess.Popen(['sudo','forever','start','app.js'],cwd=r'/home/pi/AMSCam')
sp.wait();
log('App started'); 
from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path
import json
import sys

if len(sys.argv) > 1: 
 
  # Git pull on the Python
  if(sys.argv[1]=='0'):
    sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/fireball_camera')
    sp.wait();  
    print('App Python Core updated |1');

  # Git pull on the APP
  if(sys.argv[1]=='1'):
    sp = subprocess.Popen(['git','pull'],cwd=r'/home/pi/AMSCam')
    sp.wait();
    print('App Updated |2'); 

  # Install Dependencies for the App
  if(sys.argv[1]=='2'):
    sp = subprocess.Popen(['sudo','npm','install'],cwd=r'/home/pi/AMSCam')
    sp.wait();
    print('Node Modules Updated |3'); 
   
  if(sys.argv[1]=='3'):
    sp = subprocess.Popen(['sudo', 'bower', 'install','--allow-root'],cwd=r'/home/pi/AMSCam')
    sp.wait();
    print('Bower Modules Updated |4'); 


  # Update the Calib Files (ADD EXPOSURE FOR THE FILES THAT DON'T HAVE IT YET)
  if(sys.argv[1]=='4'):
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
    print('Calibration files checked |');   
 
else:
  print('MISSING STEP')
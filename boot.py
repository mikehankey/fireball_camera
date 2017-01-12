#!/usr/bin/python3 

import os
from amscommon import read_config

# system boot script runs each time system is booted. 
# Handles first time registration and setup
# once setup simply does sanity check and logs to ams 

config = read_config()
try:
   if (config['device_lat'] != ''):
      print ("setup.")
except:
   print ("device not setup yet.")


fp = open("/home/pi/fireball_camera/booted.txt", "w")
fp.write("booted")
fp.close()

os.system("./mkdevice.py")
os.system("./logger.py reboot")

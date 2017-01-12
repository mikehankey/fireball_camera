#!/usr/bin/python3 

import os
from amscommon import read_config
import netifaces
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

try:
    eth0_ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
except:
    eth0_ip = "0.0.0.0"
try:
    wlan0_ip= netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
except:
    wlan0_ip = "0.0.0.0"

msg = "reboot " + eth0_ip + "/" + wlan0_ip
os.system("./logger.py '" + msg + "'")

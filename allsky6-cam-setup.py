#!/usr/bin/python3

# Utility for setting up the cameras for the first time. Do not run after everything is setup!
#
#

import sys
import time
import os
import requests
from amscommon import read_config


def setup_cam(cam):
   if cam == '':
      print ("ERROR NO CAM ID!")
      exit()
   else:
      print ("Turning on cam# ", cam)
      os.system("./pizero-relay.py cam_on " + str(cam))
  
   config = read_config()
   cam_ip = "192.168.1.88"

   # set the camera defaults, wait for reboot, then do it again
   os.system("./camera_defaults.py " + cam_ip)
   time.sleep(60)
   os.system("./camera_defaults.py " + cam_ip)
   time.sleep(60)

   # get the mac address
   file = open("caminfo/" + cam + ".txt", "w")
   url = "http://" + str(cam_ip) + "/cgi-bin/sysparam_cgi?user=admin&pwd="+ config['cam_pwd'] 
   print (url)
   r = requests.get(url)
   lines = r.text.split("\n") 
   for line in lines:
      if "MACAddress" in line:
         file.write("<CamID>" + str(cam) + "</CamID>\n");
         line = line.replace("\t", "");
         file.write(line)

   file.close()
   # set boot proto to dhcp
   url = "http://" + str(cam_ip) + "/cgi-bin/network_cgi?user=admin&pwd="+ config['cam_pwd'] + "&action=set&BootProto=dhcp"
   print (url)
   r = requests.get(url)
   print (r.text)
   

try:
   x, cmd, cam  = sys.argv
except:
   cmd = sys.argv[1]

if cmd == "setup":
   setup_cam(cam)
   time.sleep(1)

if cmd == "setup_all":
   setup_cam(1)
   time.sleep(60)
   setup_cam(2)
   time.sleep(60)
   setup_cam(3)
   time.sleep(60)
   setup_cam(4)
   time.sleep(60)
   setup_cam(5)
   time.sleep(60)
   setup_cam(6)
   time.sleep(60)





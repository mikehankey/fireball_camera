#!/usr/bin/python3 

import subprocess
import datetime
import os
from amscommon import read_config
import time

def ping_cam(cam_num):
   config = read_config("conf/config-" + cam_num + ".txt")
   cmd = "ping -c 1 " + config['cam_ip']
   response = os.system(cmd)
   if response == 0:
      print ("Cam is up!")
      return(1)
   else:
      print ("Cam is down!")
      return(1)

def check_files_exist(cam_num):
   bad = 0
   cmd = "find /mnt/ams2/SD -amin -5 |grep mp4 | grep cam" + str(cam_num) + " |wc -l"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output.replace("\n", "")
   if int(output) > 0:
      print ("SD cam ", str(cam_num), " is good", output)
   else:
      print ("SD cam ", str(cam_num), " is bad. Restart.", output)
      bad = bad + 1
   cmd = "find /mnt/ams2/HD -amin -5 |grep cam" + str(cam_num) + " |wc -l"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output.replace("\n", "")
   if int(output) > 0:
      print ("HD cam ", str(cam_num), " is good", output)
   else:
      print ("HD cam ", str(cam_num), " is bad. Restart.", output)
      bad = bad + 1



   return(bad)

bad = 0
for i in range (1,7):
   res = check_files_exist(i)
   if res == 1:
      bad = bad + res
print ("Total bad:", bad)
if bad >= 1:
   print ("need to stop and restart ffmpeg processes")
   os.system("./ffmpeg_record.py stop 1")

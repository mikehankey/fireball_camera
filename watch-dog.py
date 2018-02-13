#!/usr/bin/python3 

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

os.system("tail -10 /tmp/noise.log > /tmp/x")

restarted = []
fp = open("/tmp/x", "r")
for line in fp:
   line = line.replace("\n", "")
   data = line.split("|")
   if len(data) == 5:
      print (line)
      (cam_num, noise_ratio, log_date, latency, xxx) = data
      print (latency)
      if latency != "" and int(float(latency)) > 100:
         print ("Latency: ", line)
         print (restarted)
         if cam_num not in restarted:
            dist_time = datetime.datetime.now()
            log_entry = "Restarting " + str(cam_num) + "|" + str(dist_time) + "|" + str(latency) + "|"
            cmd = "/bin/echo \"" + log_entry + "\" >> /tmp/restart.log"
            print(cmd)
            os.system(cmd)

            cmd = "touch /home/ams/fireball_camera/norun" + cam_num
            print(cmd)
            os.system(cmd)

            cmd = "/home/ams/fireball_camera/allsky6-status.py stop " + cam_num
            print(cmd)
            os.system(cmd)


            cmd = "/home/ams/fireball_camera/allsky6-status.py restart_cam " + cam_num
            print(cmd)
            os.system(cmd)

            #while ping_cam(cam_num) == 0:
            #   print ("host is down")
            #   time.sleep(50)
        
            # wait for ping back after cam reboot 

            cmd = "rm /home/ams/fireball_camera/norun" + cam_num
            print(cmd)
            os.system(cmd)
            restarted.append(cam_num)


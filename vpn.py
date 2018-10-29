#!/usr/bin/python3

import subprocess
import sys
import os 
import time
def check_running():
   cmd = "ifconfig -a | grep 10.0.10 | grep -v grep | wc -l"
   print(cmd)
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   return(int(output))



running = check_running()
print (running)
if running == 0:
   cmd ="/etc/init.d/openvpn stop"
   os.system(cmd)
   time.sleep(3)
   cmd ="/etc/init.d/openvpn start"
   os.system(cmd)


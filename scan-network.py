#!/usr/bin/python3

import datetime
import os
from amscommon import read_config
import time
ip_range = "192.168.1."

def ping(ip):
   cmd = "ping -c 1 " + ip  
   response = os.system(cmd)
   if response == 0:
      print (ip, " is up!")
      return(1)
   else:
      print (ip, " is down!")
      return(1)

for i in range(1,255):
   print(i)
   ip = ip_range + str(i)
   ping(ip)

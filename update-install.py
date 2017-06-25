#!/usr/bin/python3

import os

try:
   from dateutil import parser
   du = 1
except:
   du = 0 
   print ("No dateutl!" )

if du == 0:
   os.system("sudo pip install python-dateutil")
else:
   print ("date util already installed")

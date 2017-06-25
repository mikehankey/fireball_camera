#!/usr/bin/python3

import os

try:
   from dateutil import parser
except:
   du = 0 
   print ("No dateutl!" )

if du == 0:
   os.system("sudo pip install python-dateutil")
else:
   print ("date util already installed")

#!/usr/bin/python3

import os

try:
   from dateutil import parser
except:
   du = 0 
   print ("No dateutl!" )

os.system("sudo pip install python-dateutil")

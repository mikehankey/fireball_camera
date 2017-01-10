#!/usr/bin/python3 

import sys
import os
import subprocess

def do_it_all():
   cmd = "./sense_up.py sense_up"
   output = subprocess.check_output(cmd, shell=True)
   print (output) 
   output = subprocess.check_output(cmd, shell=True)
   star_file = output.decode("utf-8")
   cmd = "./sense_up.py stack " + star_file 

   print (cmd) 
   #output = subprocess.check_output(cmd, shell=True)
   #output = output.decode("utf-8")
   #print (output)

if sys.argv[1] == 'all':
   print ("Do it all")
   do_it_all()

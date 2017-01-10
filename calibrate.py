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
   output = subprocess.check_output(cmd, shell=True)
   output = output.decode("utf-8")
   print (output)

   cal_file = star_file.replace(".avi", ".jpg")
   cmd = "./count_stars.py " + cal_file
   output = subprocess.check_output(cmd, shell=True)
   output = output.decode("utf-8")
   output = output.replace("\n", "") 
   output = output.replace(" ", "") 
   (trash, total_stars) = output.split(":")
   print (total_stars)
   if int(total_stars) > 0:
      print ("Plenty of stars. Try Plate Solve.") 
   else:
      print ("Not enough stars. Calibration Failed.") 
   

   #cmd = "./calibrate_image.py cal_file" 
   #print (cmd) 
   #output = subprocess.check_output(cmd, shell=True)
   #output = output.decode("utf-8")
   #print (output)

if sys.argv[1] == 'all':
   print ("Do it all")
   do_it_all()

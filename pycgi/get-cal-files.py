#!/usr/bin/python3
from collections import defaultdict
import random
import glob
import subprocess
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"
from pathlib import Path


def get_cal_files(day, cam):
   if cam == "all": 
      glob_dir = "/mnt/ams2/cal/*.jpg"
   else:
      glob_dir = "/mnt/ams2/cal/*-" + str(cam) + ".jpg"
   files = glob.glob(glob_dir)
   files = (sorted(files))
   json_data = "{ \"results\": [\n"
   c = 0;
   for file in files:
      if c > 0: 
         json_data = json_data + ","
      json_data = json_data + "{ \"cfile\": \"" + file + "\"}\n"
      c = c + 1
   json_data = json_data + "]}" 
   print(json_data)
print ("Content-type: text/html\n\n")
form = cgi.FieldStorage()
cam = form.getvalue('cam')
if cam is None: 
   get_cal_files("", "all")
else: 
   get_cal_files("", cam)

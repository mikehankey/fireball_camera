#!/usr/bin/python3 
import glob
import sys
import ProcessVideo as PV
import time
import os
import subprocess
import time

video_dir = "/mnt/ams/SD"
arg = sys.argv[1]

def check_running():
   cmd = "ps -aux |grep \"PV.py\" | grep -v grep | wc -l"
   print(cmd)
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   return(output)

if arg == 'batch':
   already_running = check_running()
   print (already_running)
   if int(already_running) > 2:
      print ("already running")
      exit()
   else:
      print ("not running")
   #do batch for 1 cam
   cam_num = sys.argv[2]
   files = glob.glob(video_dir + "/*.mp4")
   if len(files) == 0:
      files = glob.glob(video_dir + "/*.avi")
   for file in sorted(files):
      cur_time = int(time.time())
      st = os.stat(file)
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 
      print (file, tdiff)
      if tdiff > 1.1:
         vid = PV.ProcessVideo()
         vid.orig_video_file = file
         vid.show_video = 0
         vid.detect_stars = 0
         vid.detect_motion = 1 
         vid.make_stack = 1 
         vid.ProcessVideo()
         #vid.StackVideo()


else:
   #do 1 file 

   vid = PV.ProcessVideo()
   vid.orig_video_file = arg
   vid.detect_motion = 1 
   vid.show_video = 1 
   vid.make_stack = 1 
   vid.ProcessVideo()

#!/usr/bin/python3 
import glob
from pathlib import Path
import sys
import ProcessVideo as PV
import time
import os
import subprocess
import time

video_dir = "/mnt/ams2/SD"
arg = sys.argv[1]
cam_num = sys.argv[2]
def check_running(cam_num):
   #cmd = "ps -aux |grep \"PV.py batch + " + cam_num + " \" | grep -v grep | wc -l"
   cmd = "ps -aux |grep \"PV.py\" | grep -v grep | wc -l"
   print(cmd)
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   return(output)
if arg == 'find_HD':
   file = sys.argv[2] 
   print("FILE:", file)
   vid = PV.ProcessVideo()
   vid.orig_video_file = file
   vid.find_HD_files()
   exit()

if arg == 'batch':
   already_running = check_running(cam_num)
   print (already_running)
   if int(already_running) > 2:
      print ("already running")
      exit()
   else:
      print ("not running")
   #do batch for 1 cam
   cam_num = sys.argv[2]
   #files = glob.glob(video_dir + "/*cam" + cam_num + "*.mp4")
   #2018-03-23_02
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
      stack_file = file.replace(".mp4", "-stack.jpg")
      file_exists = Path(stack_file)
      skip = 0
      if (file_exists.is_file()):
         skip = 1

      if tdiff > 1.1 and skip == 0:

         cmd = "./fast_frames2.py " + file 
         #cmd = "./PV.py " + file + " x"
         start_time = int(time.time())
         os.system(cmd)
         end_time = int(time.time())
         elapsed = end_time - start_time
         print ("PROCESSED FILE IN: ", elapsed)
         #vid = PV.ProcessVideo()
         #vid.orig_video_file = file
         #vid.show_video = 1
         #vid.detect_stars = 0
         #vid.detect_motion = 1 
         #vid.make_stack = 1 
         #vid.ProcessVideo()
         #vid.StackVideo()

elif arg == 'crop':
   file = sys.argv[2]
   vid = PV.ProcessVideo()
   vid.orig_video_file = file
   vid.parse_file_date()
   exists = vid.load_report()
   vid.cropVideo()

else:
   #do 1 file 

   vid = PV.ProcessVideo()
   vid.orig_video_file = arg
   #vid.find_HD_video(608,711)
   #exit()
   vid.detect_motion = 1 
   vid.show_video = 1 
   vid.make_stack = 1 
   vid.ProcessVideo()

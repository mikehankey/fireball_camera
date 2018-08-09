#!/usr/bin/python3 
import glob
import ephem
from pathlib import Path
import sys
import ProcessVideo as PV
import time
import os
import subprocess
import time
from amscommon import read_config
conf = read_config("conf/config-1.txt")

def day_or_night(config, capture_date):

   obs = ephem.Observer()

   obs.pressure = 0
   obs.horizon = '-0:34'
   obs.lat = config['device_lat']
   obs.lon = config['device_lng']
   obs.date = capture_date

   sun = ephem.Sun()
   sun.compute(obs)

   (sun_alt, x,y) = str(sun.alt).split(":")

   saz = str(sun.az)
   (sun_az, x,y) = saz.split(":")
   if int(sun_alt) < -1:
      sun_status = "night"
   else:
      sun_status = "day"
   return(sun_status)


def parse_date (this_file):
   el = this_file.split("/")
   file_name = el[-1]
   file_name = file_name.replace("_", "-")
   file_name = file_name.replace(".", "-")
   xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, xext = file_name.split("-")
   cam_num = xcam_num.replace("cam", "")

   date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
   capture_date = date_str
   return(cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec)


video_dir = "/mnt/ams2/SD"
arg = sys.argv[1]
cam_num = sys.argv[2]
def check_running(cam_num):
   #cmd = "ps -aux |grep \"PV.py batch + " + cam_num + " \" | grep -v grep | wc -l"
   cmd = "ps -aux |grep \"PV.py\" | grep -v grep | wc -l"
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
   if int(already_running) > 2 :
      print ("already running")
      exit()
   #do batch for 1 cam
   cam_num = sys.argv[2]
   #files = glob.glob(video_dir + "/*cam" + cam_num + "*.mp4")
   files = glob.glob(video_dir + "/*.mp4")
   #2018-03-23_02
   #files = glob.glob(video_dir + "/*.mp4")
   if len(files) == 0:
      files = glob.glob(video_dir + "/*.avi")
   cc = 0
   for file in sorted(files, reverse=True):
        
      cur_time = int(time.time())
      st = os.stat(file)
      size = st.st_size
      print ("SIZE:", size)
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 
      stack_file = file.replace(".mp4", "-stacked.jpg")
      fail_file = file.replace(".mp4", "-fail.txt")
      wild_card = file.replace(".mp4", "*.*")
      file_exists = Path(stack_file)
      skip = 0
     
      # Remove bad file if they exist 
      if size <= 50000:
         skip = 1
         cmd = "rm " + wild_card
         os.system(cmd)
         print(cmd)

      if (file_exists.is_file()):
         skip = 1

      file_exists = Path(fail_file)
      if (file_exists.is_file()):
         skip = 1
         cmd = "rm " + wild_card
         os.system(cmd)
         print(cmd)



      if tdiff > 1.1 and skip == 0:
         (cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = parse_date(file)
         sun_status = day_or_night(conf, date_str)
         print (date_str, sun_status)
         if sun_status == "day":
            el = file.split("/")
            file_name = el[-1]
            cmd = "mv " +  file + " /mnt/ams2/SD/proc/daytime/" + file_name 
            os.system(cmd)
           
         else:
            if cc % 1 == 0:
               cmd = "./fast_frames5.py " + file 
               os.system(cmd)
               #time.sleep(15)
            #else:
            #   time.sleep(10)
            #   cmd = "./fast_frames4.py " + file 
            #   os.system(cmd)

         #vid = PV.ProcessVideo()
         #vid.orig_video_file = file
         #vid.show_video = 1
         #vid.detect_stars = 0
         #vid.detect_motion = 1 
         #vid.make_stack = 1 
         #vid.ProcessVideo()
         #vid.StackVideo()
      cc = cc + 1
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
   vid.show_video = 0 
   vid.make_stack = 1 
   vid.ProcessVideo()

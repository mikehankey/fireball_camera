#!/usr/bin/python3
import glob
import ephem
import subprocess
from pathlib import Path
import os
from amscommon import read_config

video_dir = "/mnt/ams2/SD/"
hd_video_dir = "/mnt/ams2/HD/"

def parse_date (this_file):

   el = this_file.split("/")
   file_name = el[-1]
   file_name = file_name.replace("_", "-")
   file_name = file_name.replace(".", "-")
   fnel = file_name.split("-")
   if len(fnel) == 9:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype,xext = fnel
   if len(fnel) == 8:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, xext = fnel
   cam_num = xcam_num.replace("cam", "")

   date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
   capture_date = date_str
   return(cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec)


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


def move_old_school_files():
   cmd = 'find /mnt/ams2/SD/ | grep .mp4'
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   files = output.split('\n')
   for file in files:
      el = file.split("/")
      file_name = el[-1]
      if "trim" in file:
         cmd = "mv " +  file + " /mnt/ams2/SD/meteors/" + file_name
         os.system(cmd) 
         continue 

      (cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = parse_date(file)
      sun_status = day_or_night(conf, date_str)

      date_dir = "/mnt/ams2/SD/proc/" + xyear + "-" + xmonth + "-" + xday
      file_exists = Path(date_dir)
      skip = 0
      if (file_exists.is_dir() is False):
         os.system("mkdir " + date_dir) 

      if sun_status == "day":
         cmd = "mv " +  file + " /mnt/ams2/SD/proc/daytime/" + file_name
         os.system(cmd) 
      else:
         cmd = "mv " +  file + " " + date_dir + "/" + file_name
         os.system(cmd) 
      print (cmd)

def move_processed_SD_files():

   files = glob.glob(video_dir + "*.jpg")
   
   for file in files:
      el = file.split("/")
      if "-stack.jpg" in file:
         video_file = file.replace("-stack.jpg", ".mp4")
      else: 
         video_file = file.replace("-stacked.jpg", ".mp4")
      file_name = el[-1]
      vel = video_file.split("/")
      video_file_name = vel[-1]
      print ("Stack File:", file)
      print ("Video File:", video_file)
      (cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = parse_date(file)
      sun_status = day_or_night(conf, date_str)
      print("SUN:", sun_status)

      date_dir = "/mnt/ams2/SD/proc/" + xyear + "-" + xmonth + "-" + xday
      file_exists = Path(date_dir)
      skip = 0
      if (file_exists.is_dir() is False):
         os.system("mkdir " + date_dir) 
      if sun_status == "day":
         cmd = "mv " +  file + " /mnt/ams2/SD/proc/daytime/" + file_name
         #os.system(cmd) 
         cmd = "mv " +  video_file + " /mnt/ams2/SD/proc/daytime/" + video_file_name
         #os.system(cmd) 
      else:
         if "-stacked" not in file_name:
            file_name = file_name.replace("stack", "stacked")
         cmd = "mv " +  file + " " + date_dir + "/" + file_name
         #print(cmd)
         os.system(cmd) 

         cmd = "mv " +  video_file + " " + date_dir + "/" + video_file_name
         #print(cmd)
         os.system(cmd) 
   


conf = read_config("conf/config-1.txt")
move_processed_SD_files()

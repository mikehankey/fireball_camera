#!/usr/bin/python3
import time
import glob
import ephem
import subprocess
from pathlib import Path
import os
from amscommon import read_config
import datetime
from time import mktime
from pytz import utc

video_dir = "/mnt/ams2/SD/"
hd_video_dir = "/mnt/ams2/HD/"

def parse_date (this_file):

   el = this_file.split("/")
   file_name = el[-1]
   file_name = file_name.replace("_", "-")
   file_name = file_name.replace(".", "-")
   fnel = file_name.split("-")
   #print("FILE:", file_name, len(fnel))
   if len(fnel) == 11:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype,fnum,fst,xext = fnel
   if len(fnel) == 10:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype,fnum,xext = fnel
   if len(fnel) == 9:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype, xext = fnel
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


def purge_sd_files():
   files = glob.glob(video_dir + "proc/daytime/*")
   for file in files:
      (cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = parse_date(file)
      sun_status = day_or_night(conf, date_str)
      st = os.stat(file)
      cur_time = int(time.time())
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 / 60 / 24
      if sun_status == 'day' and tdiff > 3:
         print ("File is daytime and this many days old", tdiff, file)
         os.system("rm " + file)
      #else:
      #   print ("File is nighttime and this many days old", tdiff, file)

def purge_hd_files():
   files = glob.glob(hd_video_dir + "*")
   for file in files:
      (cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = parse_date(file)
      sun_status = day_or_night(conf, date_str)
      st = os.stat(file)
      cur_time = int(time.time())
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 / 60 / 24
      if sun_status == 'day' and tdiff > 1:
         print ("File is daytime and this many days old", tdiff, file)
         print("rm " + file)
         os.system("rm " + file)
      elif tdiff > 2:
         print ("File is nighttime and this many days old will be purged.", tdiff, file)
         print("rm " + file)
         os.system("rm " + file)

def purge_SD_proc_dir():
   files = glob.glob(video_dir + "proc/*")

   for file in files:
      st = os.stat(file)
      el = file.split("/") 
      date_file = el[-1]
      if date_file != 'daytime' and date_file != 'bad':
         dir_date = datetime.datetime.strptime(date_file, "%Y-%m-%d") 
         print ("DIR DATE: ", dir_date)
         cur_time = int(time.time())
         mtime = mktime(utc.localize(dir_date).utctimetuple())

         tdiff = cur_time - mtime
         tdiff = tdiff / 60 / 60 / 24
         print (file, tdiff)
         if tdiff >= 25 and file != 'daytime':
            print ("We should delete this dir in the archive. it is this many days old:", tdiff) 
            cmd = "rm -rf " + file
            os.system(cmd)
            print(cmd)


def move_processed_SD_files():

   files = glob.glob(video_dir + "*stacked.jpg")
   #print("SUN:", sun_status)
   
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
         print(cmd)
         os.system(cmd) 
         cmd = "mv " +  video_file + " /mnt/ams2/SD/proc/daytime/" + video_file_name
         print(cmd)
         os.system(cmd) 
      else:
         if "-stacked" not in file_name:
            file_name = file_name.replace("stack", "stacked")

         cmd = "mv " +  file + " " + date_dir + "/" + file_name
         print(cmd)
         os.system(cmd) 

         cmd = "mv " +  video_file + " " + date_dir + "/" + video_file_name
         print(cmd)
         os.system(cmd) 
  
         wild_card = video_file.replace(".mp4", "*")
         cmd = "mv " +  wild_card + " " + date_dir + "/" 
         os.system(cmd) 
   


conf = read_config("conf/config-1.txt")
move_processed_SD_files()
purge_hd_files()
purge_sd_files()
purge_SD_proc_dir()

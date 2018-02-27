#!/usr/bin/python3

from PIL import Image
import cv2
import glob
import sys
import numpy as np
import datetime
import os
import time
from pathlib import Path
from amscommon import read_config 

#path = sys.argv[1]

# This script runs once a day preferably a little after sunrise. 
#
# The script will mv all of the files in the time_lapse directory
# into the proper camera sub folder
# It will then run the video-from-still.py cam_time_lapse_folder for
# each camera
# once the time lapse video is created it will move all of the files to a trash folder. 
# when everything is finished it will delete all files in the trash folder older than 25 hours. 

# The first few frames of the script should show the following info:
# AllSky6 24 Hour Summary For Observatory Name
# Camera Operator: Mike Farmer
# Period: 2018-02-06 12:00:00 - 2018-02-06 12:00:00 UTC
# Camera #: 1
# Device ID: AMS18
# Longitude: 38.99
# Latitude: -111.11
# Altitude: 400
# Pointing Azimuth: 0
# Pointing Elevation: 0
# Total Motion Events: 25
# Day Time Events: 15
# Night Time Events: 10 
# Calibration Events: 7
# Distortion Events: 3
# Suspect Events: 2

def upload_to_youtube(file_date, cam_num, title, desc):
   cmd = "cd google; /usr/bin/python upload-video.py --file=/var/www/html/out/time_lapse/videos/" + file_date + "-" + cam_num + ".avi --title=\"" + title +"\" --desc=\"" + desc +"\""
   print (cmd)
   os.system(cmd)

def email_report(to, report):
   print ("YOYO")

def mkdirs():
   os.system("mkdir /var/www/html/out/calvid")
   os.system("mkdir /var/www/html/out/dist")
   os.system("mkdir /var/www/html/out/time_lapse")
   os.system("mkdir /var/www/html/out/time_lapse/trash")
   os.system("mkdir /var/www/html/out/time_lapse/videos")
   os.system("mkdir /var/www/html/out/time_lapse/1")
   os.system("mkdir /var/www/html/out/time_lapse/2")
   os.system("mkdir /var/www/html/out/time_lapse/3")
   os.system("mkdir /var/www/html/out/time_lapse/4")
   os.system("mkdir /var/www/html/out/time_lapse/5")
   os.system("mkdir /var/www/html/out/time_lapse/6")

def move_to_trash(cam_num):
   cmd = "mv /var/www/html/out/time_lapse/" + cam_num + "/*.jpg /var/www/html/out/time_lapse/trash/"
   print (cmd)
   os.system(cmd)

def make_time_lapse(cam_num):
   # if the timelapse file for today doesn't already exist then make it. 
   datestr = datetime.datetime.now()
   datestr = datestr.strftime("%Y%m%d")
   datestr = datestr + "-" + cam_num + ".avi"

   outfile = "/var/www/html/out/time_lapse/videos/" + datestr
   file_exists = Path(outfile)
   if (file_exists.is_file()):
      print("This file has already been processed.")
   else:
      print("Making timelapse video please wait...")
      cmd = "./video-from-still.py /var/www/html/out/time_lapse/" + cam_num
      os.system(cmd)


def sort_files(cam_num):
   cmd = "mv /var/www/html/out/time_lapse/*-" + cam_num + ".jpg /var/www/html/out/time_lapse/" + cam_num
   print (cmd)
   os.system(cmd)

# do the reports for each camera. 

def do_24_hour_report(cam_num, report):
   file_list = []
   cur_time = int(time.time())
   yest_time = int(time.time()- 86400)
   stop_time = datetime.datetime.fromtimestamp(int(cur_time)).strftime("%Y-%m-%d %H:%M:%S")
   start_time = datetime.datetime.fromtimestamp(int(yest_time)).strftime("%Y-%m-%d %H:%M:%S")
   
   # check the following dirs: false, maybe, dist, calvid
   report = report + "-------------------\n"
   report = report + "-----CAMERA #" + cam_num + "-----\n"
   report = report + "-------------------\n"
   count = 0 
   path = "/var/www/html/out/maybe"
   report = report + "-----Nighttime Events-----\n"
   for filename in (glob.glob(path + '/*-' + cam_num + '.avi')):
      st = os.stat(filename)
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 / 60 / 24
      if tdiff <= 1.1: 
         report = report + "   " + filename + "\n"
         file_list.append(filename)
         count = count + 1
   report = report + "   " + str(count) + " nighttime captures\n"
   report = report + "--------------------------\n"

   count = 0 
   path = "/var/www/html/out/false"
   report = report + "-----Daytime Events-----\n"
   for filename in (glob.glob(path + '/*-' + cam_num + '.avi')):
      st = os.stat(filename)
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 / 60 / 24
      if tdiff <= 1.1: 
         report = report + "   " + filename + "\n"
         file_list.append(filename)
         count = count + 1
   report = report + "   " + str(count) + " daytime captures\n"
   report = report + "--------------------------\n"

   count = 0 
   report = report + "-----Calibration Events-----\n"
   path = "/var/www/html/out/calvid"
   for filename in (glob.glob(path + '/*-' + cam_num + '.avi')):
      st = os.stat(filename)
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 / 60 / 24
      if tdiff <= 1.1: 
         report = report + "   " + filename + "\n"
         file_list.append(filename)
         count = count + 1
   report = report + "   " + str(count) + " calibration captures\n"
   report = report + "--------------------------\n"

   count = 0 
   path = "/var/www/html/out/dist"
   report = report + "-----Distortion Events-----\n"
   for filename in (glob.glob(path + '/*-' + cam_num + '.avi')):
      st = os.stat(filename)
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 / 60 / 24
      if tdiff <= 1.1: 
         report = report + "   " + filename + "\n"
         file_list.append(filename)
         count = count + 1
   report = report + "   " + str(count) + " distorton captures\n"
   report = report + "--------------------------\n"
   return(report)

cur_time = int(time.time())
yest_time = int(time.time()- 86400)
stop_time = datetime.datetime.fromtimestamp(int(cur_time)).strftime("%Y-%m-%d %H:%M:%S")
start_time = datetime.datetime.fromtimestamp(int(yest_time)).strftime("%Y-%m-%d %H:%M:%S")

try:
   config = read_config("conf/config-1.txt")
   config = read_config(config_file)
   single = 0
except:
   config = read_config("config.txt")
   cam_num = config['cam_num']
   single = 1


report = "AllSky6 24 Hour Report for " + config['obs_name'] + "\n"
report = report + "Period:" + str(start_time) + " to " + str(stop_time) + "\n"
report = report + "Camera Operator: " + config['first_name'] + " " + config['last_name'] + "\n"
report = report + "Latitude : " + config['device_lat'] + "\n"
report = report + "Longitude: " + config['device_lng'] + "\n"
report = report + "Altitude: " + config['device_alt'] + "\n"

if single == 0: 
   sort_files("1")
   sort_files("2")
   sort_files("3")
   sort_files("4")
   sort_files("5")
   sort_files("6")

   report = do_24_hour_report("1", report)
   report = do_24_hour_report("2", report)
   report = do_24_hour_report("3", report)
   report = do_24_hour_report("4", report)
   report = do_24_hour_report("5", report)
   report = do_24_hour_report("6", report)

   datestr = datetime.datetime.now()
   datestr = datestr.strftime("%Y%m%d")
   rpt_file = datestr + "-report.txt"
   fp = open("/var/www/html/out/time_lapse/videos/" + rpt_file, "w")
   fp.write(report)
   fp.close()




   make_time_lapse("1")
   make_time_lapse("2")
   make_time_lapse("3")
   make_time_lapse("4")
   make_time_lapse("5")
   make_time_lapse("6")

   move_to_trash("1")
   move_to_trash("2")
   move_to_trash("3")
   move_to_trash("4")
   move_to_trash("5")
   move_to_trash("6")


   for x in range(1,7): 
      print (x)
      cam_num = str(x)
      title = config['obs_name'] + " CAM#" + str(cam_num) + " timelapse for " + stop_time + " to " + start_time  
      desc = "AMS #" + config['device_id'] + " Operated by " + config['first_name'] + " " + config['last_name'] + " in " + config['city_name'] + "," + config['state_name']
      upload_to_youtube(datestr, cam_num, title, desc)
else:
   print("do 1 file")
   sort_files(str(cam_num))
   report = do_24_hour_report(str(cam_num), report)

   datestr = datetime.datetime.now()
   datestr = datestr.strftime("%Y%m%d")
   rpt_file = datestr + "-report.txt"
   fp = open("/var/www/html/out/time_lapse/videos/" + rpt_file, "w")
   fp.write(report)
   fp.close()
   make_time_lapse(str(cam_num))
   title = config['obs_name'] + " CAM#" + str(cam_num) + " timelapse for " + stop_time + " to " + start_time  
   desc = "AMS #" + config['device_id'] + " Operated by " + config['first_name'] + " " + config['last_name'] + " in " + config['city_name'] + "," + config['state_name']
   move_to_trash(cam_num)
   upload_to_youtube(datestr, cam_num, title, desc)


#clean_trash()

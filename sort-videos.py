#!/usr/bin/python

import glob
import errno    
import os
import ephem
from amscommon import read_config

def parse_file_date(file_name):
   el = file_name.split("/")
   file_name = el[-1]

   year = file_name[0:4]
   month = file_name[4:6]
   day = file_name[6:8]
   hour = file_name[8:10]
   min = file_name[10:12]
   sec = file_name[12:14]
   #date_str = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec
   date_str = year + "/" + month + "/" + day + " " + hour + ":" + min + ":" + sec
   return(date_str)

def day_or_night(config, video_date):


   obs = ephem.Observer()
   obs.pressure = 0
   obs.horizon = '-0:34'
   obs.lat = config['device_lat']
   obs.lon = config['device_lng']
   obs.date = video_date

   sun = ephem.Sun()
   sun.compute(obs)

   (sun_alt, x,y) = str(sun.alt).split(":")
   print ("Date: %s" % (video_date))
   print ("Sun Alt: %s" % (sun_alt))

   saz = str(sun.az)
   (sun_az, x,y) = saz.split(":")
   #print ("SUN AZ IS : %s" % sun_az)

   if int(sun_alt) < -5:
      status = "night"
   else:
      status = "day"
   return(status)

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

mkdir("/var/www/html/out/false/day")
mkdir("/var/www/html/out/false/night")
mkdir("/var/www/html/out/maybe/day")
mkdir("/var/www/html/out/maybe/night")

config = read_config()
files = glob.glob("/var/www/html/out/false/*.avi")
status = ""
for file in files:
   file_date = parse_file_date(file)
   status = day_or_night(config, file_date)
   el = file.split("/")
   file_name = el[-1]
   dir = file.replace(file_name, "")
   new_dir = dir + "/" + status + "/"
   cp_str = file_name.replace(".avi", "*")
   print (file, file_date, status)
   cmd = "mv " + dir + cp_str + " " + new_dir  
   print (cmd)
   os.system(cmd)

#!/usr/bin/python3
from collections import defaultdict
import re
import random
import subprocess
import cgi
import cgitb
from pathlib import Path
import datetime
import glob
import os

def convert_filename_to_date_cam(file):
   el = file.split("/")
   filename = el[-1]
   f_date, f_time_cam = filename.split("_")
   el = f_time_cam.split("-")
   if len(el) == 4:
     f_h, f_m, f_s, f_cam = f_time_cam.split("-")
     f_cam = f_cam.replace(".mp4", "")
     f_date_str = f_date + " " + f_h + ":" + f_m + ":" + f_s
     f_datetime = datetime.datetime.strptime(f_date_str, "%Y-%m-%d %H:%M:%S")
   return(f_datetime, f_cam, f_date, f_h, f_m, f_s)

def get_cal_files(cam = "", date = ""):
   cal_dir = "/mnt/ams2/cal/"
   file_list = []
   #start_datetime = datetime.datetime.strptime(start, "%Y-%m-%d_%H:%M:%S")
   #end_datetime = datetime.datetime.strptime(end, "%Y-%m-%d_%H:%M:%S")
   if cam != "":
      cam_str = "-" + str(cam)
   else :
      cam_str = ""
   for cal_file in sorted((glob.glob(cal_dir + date + "*" + cam_str + "*.jpg"))):
      #(f_datetime, f_cam, f_date, f_h, f_m, f_s) = convert_filename_to_date_cam(tl_file)
      file_list.append(cal_file)
   return(file_list)

def workon(cal_file):
   print ("<IMG SRC=" + cal_file + " width=1280 height=720>")
   print ("<a href=sro-cal.py?act=plate_solve&cal_file=" + cal_file + ">Plate Solve</a>")

def check_running():
   cmd = "ps -aux |grep calibrate_image.py | grep -v grep | wc -l"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   print(output)

   if output > 0:
      return(1)
   else:
      return(0)

def check_if_solved(cal_file):
   cal_wild = cal_file.replace(".jpg", "*")
   astr_files = []
   solved = 0
   for astr_file in sorted((glob.glob(cal_wild))):
      if 'wcs' in  astr_file:
         print("This image has been solved.")
         solved = 1
      astr_files.append(astr_file)
   return(solved, astr_files)


def plate_solve(cal_file):
   # check to see if the calibration is currently running
   running = check_running()
   solved, astr_files = check_if_solved(cal_file)
   print(solved, running)
   if running == 0 and solved == 0:
      print ("<HR>")
      cmd = "cd /home/ams/fireball_camera; ./calibrate_image.py " + cal_file + " & > /dev/null 2>&1"
      print(cmd)
      os.system(cmd)
      print("Starting plate solve...")
   elif running > 0:
      print ("This is already running.")
   elif solved == 1:
      print ("This has been solved.")
      print ("<PRE>")
      for astr_file in astr_files:
         print ("<a href=" + astr_file + ">" + astr_file + "</a><br>")

   else: 
      print ("not sure what to do here...")
   

def main():
   print("Content-type: text/html\n\n")

   form = cgi.FieldStorage()
   date_match = form.getvalue('date')
   cam_num = form.getvalue('cam_num')
   act = form.getvalue('act')
   if act == None :
      browse(cam_num, date_match)
   if act == "workon":
      cal_file = form.getvalue('cal_file')
      workon(cal_file)
   if act == "plate_solve":
      cal_file = form.getvalue('cal_file')
      plate_solve(cal_file)


def browse(cam_num, date_match):
   if date_match is None:
      date_match = ""
   if cam_num is None:
      cam_num = ""
   cal_files = get_cal_files(cam_num, date_match)


   for cal_file in cal_files:
      print ("<a href=sro-cal.py?act=workon&cal_file=" + cal_file + "><img src=" + cal_file + " width=320 height=170></a> <BR>")

main()

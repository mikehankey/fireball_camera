#!/usr/bin/python3 
import sys
import subprocess 
import time
import os

def proc_count(cam_num):
   cmd = "ps -aux |grep \"capture-hd.py " + cam_num + "\" | grep -v grep | wc -l"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   return(int(output))

def check_running(cam_num):
   cmd = "ps -aux |grep \"capture-hd.py " + cam_num + "\" | grep -v grep | wc -l"
   print (cmd)
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   print (output)

   if output == 4 or output == 5 or output == 6:
      return(1)
   else:
      return(0)

def check_latest(cam_num):
   print ("Checking latest...")
   cmd = "find /var/www/html/out/latest" + cam_num + ".jpg -mmin -3"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = str(output.replace("\n", ""))
   if output == "":
      print ("Latest is too old or missing, need to restart capture for cam " + cam_num)
      return(0)
   else:
      print ("All good latest" + cam_num + ".jpg updated within last 3 minutes")
      return(1)



def start_capture(cam_num):
   status = check_running(cam_num)
   if int(status) == 0:
      count = proc_count(cam_num)
      if count > 0: 
         stop_capture(cam_num)
         time.sleep(5)

      cmd = "./capture-hd.py " + cam_num + " >/dev/null &"
      print (cmd)
      os.system(cmd)
   
   

def stop_capture(cam_num):
   print ("Stopping capture for ", cam_num)
   count = proc_count(cam_num)
   if count >= 1:
      cmd = "kill -9 `ps -aux | grep \"capture-hd.py " + cam_num + "\" |grep -v grep| awk '{print $2}'`"
      output = subprocess.check_output(cmd, shell=True).decode("utf-8")
      print (output)


def check_cam(cam_num):
   status = check_running(cam_num)
   if (status == 1):
      print ("Cam " + cam_num + " is running")
      latest = check_latest(cam_num)
      if (latest == 1):
         print ("Cam latest" + cam_num + " is fine")
      else:   
         print ("Cam latest" + cam_num + " is too old")
         stop_capture(cam_num)
         time.sleep(5)
         start_capture(cam_num)
   else:   
      print ("Cam " + cam_num + " is NOT running")
      start_capture(cam_num)

do_all = 0
cmd = ""
try: 
   cmd = sys.argv[1]
   cam_num = sys.argv[2]
except: 
   do_all = 1

if (cmd == "stop"):
   stop_capture(cam_num)
if (cmd == "start"):
   start_capture(cam_num)
if (cmd == "status"):
   check_cam(cam_num)

if do_all == 1:
   status = check_cam("1")
   status = check_cam("2")
   status = check_cam("3")
   status = check_cam("4")
   status = check_cam("5")
   status = check_cam("6")




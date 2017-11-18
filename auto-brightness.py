#!/usr/bin/python3
import subprocess
import numpy as np
from pathlib import Path
import requests
import cv2
import os
import time
import datetime
import sys
from collections import deque
import iproc
from amscommon import read_sun, read_config
from collections import defaultdict

def get_settings(config):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=get&user=admin&pwd=" + config['cam_pwd'] + "&action=get&channel=0"
   settings = defaultdict()
   r = requests.get(url)
   resp = r.text
   for line in resp.splitlines():
      (set, val) = line.split("=")
      settings[set] = val
   return(settings)


def set_setting(config, setting, value):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&action=get&channel=0&" + setting + "=" + str(value)
   r = requests.get(url)
   return(r.text)

def get_cap(config):
   cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1")

   _ , frame = cap.read()
   cv2.imwrite("test.jpg", frame)
   cap.release()

try:
   cal_on = int(sys.argv[1]);
   print ("Autobrightness Calibration")
except:
   print ("Autobrightness")
   cal_on = 0

config = read_config()

not_ok = 1

while not_ok == 1:
   settings = get_settings(config)
   print("Current Brightness Setting:", settings['Brightness'])
   get_cap(config)


   cmd = "convert test.jpg -colorspace Gray -format \"%[mean]\" info: "
   magic = str(subprocess.check_output(cmd, shell=True))
   magic = magic.replace("b", "")
   magic = magic.replace("'", "")
   magic = float(magic)
   print ("Mean Image Brightness:", magic)

   sun_info = read_sun()

   magic_dark_max = 5000
   magic_dark_min = 4000
   if cal_on == 1: 
      print ("Cal ON!")
      magic_dark_max = 6800
      magic_dark_min = 5800
   magic_day_max = 40000
   magic_day_min = 30000
   if sun_info['status'] == 'dusk' or sun_info['status'] == 'dawn': 
      magic_day_max = 20000 
      magic_day_max = 10000 

 
   diff = magic_day_max - magic
   if diff >= 1500 or diff <= -1500:
      factor = 10 
   else:
      factor = 5;
   if diff <= 800 and diff >= -800: 
      factor = 2;
   
   if int(sun_info['dark']) != 1:
      if magic > magic_day_max:
         print ("image is too bright for ", sun_info['status'], ", lower brightness")
         new_brightness = int(settings['Brightness']) - factor
         set_setting(config, "Brightness", new_brightness)
      elif magic < magic_day_min:
         print ("image is too dark for ", sun_info['status'], ", increase brightness")
         new_brightness = int(settings['Brightness']) + factor
         set_setting(config, "Brightness", new_brightness)
      else: 
         not_ok = 0
   else:
      if magic > magic_dark_max:
         print ("image is too bright for ", sun_info['status'], ", lower brightness")
         new_brightness = int(settings['Brightness']) - factor
         set_setting(config, "Brightness", new_brightness)
      elif magic < magic_dark_min:
         print ("image is too dark for ", sun_info['status'], ", increase brightness")
         new_brightness = int(settings['Brightness']) + factor
         set_setting(config, "Brightness", new_brightness)
      else: 
         not_ok = 0
         print ("Brightness is fine.")
   time.sleep(2)


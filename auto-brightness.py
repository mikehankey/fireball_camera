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
   if int(sun_info['dark']) != 1:
      if magic > 40000:
         print ("image is too bright, lower brightness")
         new_brightness = int(settings['Brightness']) - 5
         set_setting(config, "Brightness", new_brightness)
      elif magic < 37000:
         print ("Image is too dark for daytime.")
         new_brightness = int(settings['Brightness']) + 5
         set_setting(config, "Brightness", new_brightness)
      else: 
         not_ok = 0
   else:
      if magic > 3000:
         print ("image is too bright, lower brightness")
         new_brightness = int(settings['Brightness']) - 5
         set_setting(config, "Brightness", new_brightness)
      elif magic < 1500:
         print ("Image is too dark for daytime.")
         new_brightness = int(settings['Brightness']) + 5
         set_setting(config, "Brightness", new_brightness)
      else: 
         not_ok = 0
         print ("Brightness is fine.")



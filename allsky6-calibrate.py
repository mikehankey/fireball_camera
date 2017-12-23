#!/usr/bin/python3
from collections import defaultdict
from PIL import Image, ImageChops
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


def get_settings(config):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=get&user=admin&pwd=" + config['cam_pwd'] + "&action=get&channel=0"
   print (url)
   settings = defaultdict()
   r = requests.get(url)
   resp = r.text
   for line in resp.splitlines():
      (set, val) = line.split("=")
      settings[set] = val
   return(settings)

def set_special(config, field, value):
   url = "http://" + str(config['cam_ip']) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=" + str(field) + "&paramctrl=" + str(value) + "&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

def custom_settings (mode, config):
   file = open("/home/pi/fireball_camera/cam_calib/"+mode, "r")
   for line in file:
      line = line.strip('\n')
      c = line.index('=')
      config[line[0:c]] = line[c+1:]
   return(config)

def set_setting(config, setting, value):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&action=get&channel=0&" + setting + "=" + str(value)
   r = requests.get(url)
   return(r.text)
 

def get_calibration_frames(config_file, cam_num):
   config = read_config(config_file)
   prev_settings = get_settings(config)
   #print (prev_settings)
   #exit();
   settings = custom_settings("Calibration", config) 
   fp = open("/home/pi/fireball_camera/calnow" + str(cam_num), "w")


   # set brightness
   set_setting(config, "Brightness", settings['Brightness'])
   print ("setting brightness to ", settings['Brightness'])
   # set BLC
   set_special(config, "1017", settings['BLC'])
   print ("setting BLC to ", settings['BLC'])
 
   # set Gamma
   set_setting(config, "Gamma", config['Gamma'])
   print ("setting Gamma to ", settings['Gamma'])

   # set contrast
   set_setting(config, "Contrast", settings['Contrast'])
   time.sleep(2)
   print ("setting Contrast to ", settings['Contrast'])

   # sense up
   r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=25&paramstep=0&paramreserved=0&")
   time.sleep(3)
   cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1")

   cv2.setUseOptimized(True)
   #lock = open("/home/pi/fireball_camera/calibrate.txt", "w")
   time_start = time.time()
   time.sleep(3)

   _ , frame = cap.read()
   final_image = Image.fromarray(frame)
   frame_img = Image.fromarray(frame)
   frame_sz = cv2.resize(frame_img, (0,0), fx=1, fy=.75)
   cv2.imwrite("/var/www/html/out/temp_upload/cal1.jpg", frame)
   final_image=ImageChops.lighter(final_image,frame_img)
   time.sleep(1)

   _ , frame = cap.read()
   frame_img = Image.fromarray(frame)
   frame_sz = cv2.resize(frame_img, (0,0), fx=1, fy=.75)
   final_image=ImageChops.lighter(final_image,frame_img)
   cv2.imwrite("/var/www/html/out/temp_upload/cal2.jpg", frame)
   time.sleep(1)

   _ , frame = cap.read()
   frame_img = Image.fromarray(frame)
   frame_sz = cv2.resize(frame_img, (0,0), fx=1, fy=.75)
   final_image=ImageChops.lighter(final_image,frame_img)
   cv2.imwrite("/var/www/html/out/temp_upload/cal3.jpg", frame)

   for i in range(0, 7, 1):
      _ , frame = cap.read()
      frame_img = Image.fromarray(frame)
      final_image=ImageChops.lighter(final_image,frame_img)

   final_image = Image.fromarray(frame)
  

   #out_file = "/var/www/html/out/temp_upload/stack.jpg"

   frame_time = time.time()
   format_time = datetime.datetime.fromtimestamp(int(frame_time)).strftime("%Y%m%d%H%M%S")
   out_file = "{}/{}-{}.jpg".format("/var/www/html/out/cal", format_time, cam_num)
   final_image.save(out_file, "JPEG")

   # sense camera down
   r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=50&paramstep=0&paramreserved=0&")
   cap.release()

   # set BLC
   set_special(config, "1017", "0")
   # set brightness contrast gamma and BLC back to original setting before calibration
   set_setting(config, "Contrast", prev_settings['Contrast'])
   print ("setting brightness back to ", prev_settings['Brightness'])
   set_setting(config, "Brightness", prev_settings['Brightness'])
   set_setting(config, "Gamma", prev_settings['Gamma'])

   time.sleep(3)
   os.system("rm /home/pi/fireball_camera/calnow"+str(cam_num))

   os.system("/home/pi/fireball_camera/camera-settings.py " + str(cam_num))
   return(1)

def stack_calibration_video(outfile):
   print ("Done")

 

cmd = sys.argv[1]
sun_info = read_sun()
try:
   cam_num = sys.argv[2]
   config_file = "conf/config-" + cam_num + ".txt"
   #config = read_config(config_file)
except:
   #config = read_config(config_file)
   config_file = ""



if cmd == 'sense_up':
   if int(sun_info['dark']) != 1:
      print ("It must be dark to sense up.")
      exit()
   if cam_num != "all": 
      status = get_calibration_frames(config_file, cam_num)
   else:
      for i in range(1,7,1):
         cam_num = str(i)
         config_file = "conf/config-" + cam_num + ".txt"
         status = get_calibration_frames(config_file, cam_num)

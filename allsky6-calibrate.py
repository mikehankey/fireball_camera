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

def focus(config_file, cam_num) :
   config = {}
   cv2.namedWindow('pepe')
   config = read_config(config_file)

   mask_file = "conf/mask-" + str(cam_num) + ".txt"
   file_exists = Path(mask_file)
   print ("MASK FILE: ", mask_file)
   mask_exists = 0
   if (file_exists.is_file()):
      print("File found.")
      ms = open(mask_file)
      for lines in ms:
         line, jk = lines.split("\n")
         exec(line)
      ms.close()
      #mask_exists = 1
      #(sm_min_x, sm_max_x, sm_min_y, sm_max_y) = still_mask


   #config['cam_ip'] = ip
   cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_0")
   for fc in range(0,10000):
      _ , frame = cap.read()       
      if frame is not None:
         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         frame[680:720, 0:620] = [0]
         frame[580:720, 0:1280] = [0]
         if mask_exists == 1:
            frame[sm_min_y:sm_max_y, sm_min_x:sm_max_x] = [0]
         max_px = np.amax(frame)
         _, threshold = cv2.threshold(frame, max_px - 5, 255, cv2.THRESH_BINARY)
         (_, cnts, xx) = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         if len(cnts) > 0:
            x,y,w,h = cv2.boundingRect(cnts[0])
            cv2.rectangle(frame, (x-5,y-5), (x+w+5, y+h+5), (255),1)
            crop = frame[y-20:y+20, x-20:x+20] 
            _, crop_threshold = cv2.threshold(crop, max_px - 15, 255, cv2.THRESH_BINARY)
            #(_, cnts2, xx) = cv2.findContours(crop.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #x,y,w,h = cv2.boundingRect(cnts2[0])

            if (fc % 10 == 0): 
               print(w,h)

            showme = cv2.resize(crop, (0,0), fx=2.5, fy=2.5)
            #showme = cv2.resize(frame, (0,0), fx=.5, fy=.5)
            #showme = cv2.resize(threshold, (0,0), fx=.5, fy=.5)
            cv2.imshow('pepe', showme)
            cv2.waitKey(1)


def read_noise(config_file, cam_num) :
   #cv2.namedWindow('pepe')

   last_frame = None
   config = read_config(config_file)
   cur_settings = get_settings(config)
   new_brightness = int(cur_settings['Brightness'])
   cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1")
   print (config['cam_ip'])

   fcnn = 0
   nr = 0
   nrfc = 0
   nrc = 0
   cc = 0
   for fc in range(0,1000):
      _ , frame = cap.read()
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

      frame_time = time.time()
      format_time = datetime.datetime.fromtimestamp(int(frame_time)).strftime("%Y%m%d%H%M%S")
      if frame is not None:
         #frame[680:720, 0:620] = [255]
         #frame[340:360, 0:310] = [255]
         frame[460:480, 0:310] = [255]



      if last_frame is not None and fc > 10: 
         image_diff = cv2.absdiff(last_frame, frame,)
         _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY) 
         noise = threshold.sum()
         if (noise > 0): 
            nrc = nrc + 1
         if cc == 150:
            nr = nrc / nrfc
            print ("Noise ratio is: ", nrc, nrfc, nr)
            nrc = 0
            nrfc = 0
            cc = 0
            if .05 <= nr <= .15: 
               print ("brightness is good.", new_brightness)   
               return()
            if nr > .05:
               print ("Too much noise, lower brightness")
               if nr > .4:
                  new_brightness = new_brightness - 10
               else:
                  new_brightness = new_brightness - 2
               set_setting(config, "Brightness", new_brightness)
               print ("New Brightness", new_brightness) 
               if new_brightness < 60:
                  exit()
            else: 
               print ("not enough noise, increase brightness")
               new_brightness = new_brightness + 5
               set_setting(config, "Brightness", new_brightness)
               print ("New Brightness", new_brightness)
            time.sleep(1)

         #cv2.imshow('pepe', threshold)
         #cv2.imshow('pepe', frame)
         #cv2.waitKey(1)
         cc = cc + 1 
  
      last_frame = frame
      nrfc = nrfc + 1




def get_calibration_frames(config_file, cam_num):
   config = read_config(config_file)
   prev_settings = get_settings(config)
   #print (prev_settings)
   #exit();
   settings = custom_settings("Calibration", config) 
   fp = open("/home/pi/fireball_camera/calnow" + str(cam_num), "w")


   # set brightness
   #set_setting(config, "Brightness", settings['Brightness'])
   #print ("setting brightness to ", settings['Brightness'])
   # set BLC
   #set_special(config, "1017", settings['BLC'])
   #print ("setting BLC to ", settings['BLC'])
 
   # set Gamma
   #set_setting(config, "Gamma", config['Gamma'])
   #print ("setting Gamma to ", settings['Gamma'])

   # set contrast
   #set_setting(config, "Contrast", settings['Contrast'])
   #time.sleep(2)
   #print ("setting Contrast to ", settings['Contrast'])

   # sense up
   r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=25&paramstep=0&paramreserved=0&")
   time.sleep(3)
   cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1")

   #read_noise(config_file, cam_num)

   cv2.setUseOptimized(True)
   #lock = open("/home/pi/fireball_camera/calibrate.txt", "w")
   time_start = time.time()
   time.sleep(3)

   _ , frame = cap.read()
   frame = cv2.resize(frame, (0,0), fx=1, fy=.75)
   final_image = Image.fromarray(frame)
   frame_img = Image.fromarray(frame)
   cv2.imwrite("/var/www/html/out/temp_upload/cal1.jpg", frame)
   final_image=ImageChops.lighter(final_image,frame_img)
   time.sleep(1)

   _ , frame = cap.read()
   frame = cv2.resize(frame, (0,0), fx=1, fy=.75)
   frame_img = Image.fromarray(frame)
   final_image=ImageChops.lighter(final_image,frame_img)
   cv2.imwrite("/var/www/html/out/temp_upload/cal2.jpg", frame)
   time.sleep(1)

   _ , frame = cap.read()
   frame = cv2.resize(frame, (0,0), fx=1, fy=.75)
   frame_img = Image.fromarray(frame)
   final_image=ImageChops.lighter(final_image,frame_img)
   cv2.imwrite("/var/www/html/out/temp_upload/cal3.jpg", frame)

   for i in range(0, 30, 1):
      _ , frame = cap.read()
      frame = cv2.resize(frame, (0,0), fx=1, fy=.75)
      frame_img = Image.fromarray(frame)
      final_image=ImageChops.lighter(final_image,frame_img)

   final_image = Image.fromarray(frame)
  

   #out_file = "/var/www/html/out/temp_upload/stack.jpg"

   frame_time = time.time()
   format_time = datetime.datetime.fromtimestamp(int(frame_time)).strftime("%Y%m%d%H%M%S")
   out_file = "{}/{}-{}.jpg".format("/var/www/html/out/cal", format_time, cam_num)
   final_image.save(out_file, "JPEG")

   time.sleep(10)
   # sense camera down
   r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=50&paramstep=0&paramreserved=0&")
   cap.release()

   # set BLC
   #set_special(config, "1017", "30")
   # set brightness contrast gamma and BLC back to original setting before calibration
   #set_setting(config, "Contrast", prev_settings['Contrast'])
   #print ("setting brightness back to ", prev_settings['Brightness'])
   #set_setting(config, "Brightness", prev_settings['Brightness'])
   #set_setting(config, "Gamma", prev_settings['Gamma'])

   time.sleep(3)
   os.system("rm /home/pi/fireball_camera/calnow"+str(cam_num))

   #os.system("/home/pi/fireball_camera/camera-settings.py " + str(cam_num))
   #return(1)

def stack_calibration_video(outfile):
   print ("Done")

 

cmd = sys.argv[1]
sun_info = read_sun()
try:
   cam_num = sys.argv[2]
   config_file = "conf/config-" + cam_num + ".txt"
   #config = read_config(config_file)
except:
   config_file = "config.txt"
   config = read_config(config_file)
   cam_num = config['cam_num']

if cmd == 'focus':
   print ("FOCUS")
   focus(config_file, cam_num)

if cmd == 'read_noise':
   read_noise(config_file, cam_num)

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

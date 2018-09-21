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


def get_latest_pic(cam_num, cap_ip):
   if cam_ip == "":
      config_file = "conf/config-" + str(cam_num) + ".txt"
      outfile = "/var/www/html/out/latest-" + str(cam_num) + ".jpg"

      config = read_config(config_file)
   else :
      config = {}
      config['cam_ip'] = cam_ip
      el = cam_ip.split(".")
      outfile = "/var/www/html/out/latest-" + str(el[-1]) + ".jpg"
   cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_0")


   cv2.setUseOptimized(True)

   _ , frame = cap.read()
   #frame = cv2.resize(frame, (0,0), fx=1, fy=.75)

   cv2.imwrite(outfile, frame)  


cam_num = sys.argv[1]
if len(sys.argv) == 3:
   cam_ip = sys.argv[2]
else:
   cam_ip = ""

get_latest_pic(cam_num, cam_ip)

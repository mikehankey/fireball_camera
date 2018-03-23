#!/usr/bin/python3

from PIL import Image
import cv2
import glob
import sys
import numpy as np
import datetime
path = sys.argv[1]

el = path.split("/")
cam_num = el[-1]
if cam_num == "":
   cam_num = el[-2]

datestr = datetime.datetime.now()
datestr = datestr.strftime("%Y%m%d")
datestr = datestr + "-" + cam_num + ".avi"

outfile = "/var/www/html/out/time_lapse/videos/" + datestr
#outfile = "test.avi"


image_list = []
file_list = []
sorted_list = []
for filename in (glob.glob(path + '/*.jpg')): 
    file_list.append(filename)

open_cv_image = cv2.imread(filename,1)
height , width, chan =  open_cv_image.shape

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'H264')
out = cv2.VideoWriter(outfile,fourcc, 25, (width,height),1)

sorted_list = sorted(file_list)
count = 0
for filename in sorted_list:
    if count % 1 == 0:
       open_cv_image = cv2.imread(filename,1)
       h , w, c=  open_cv_image.shape
       if h == height and w == width and c == chan:
          print ("adding", filename)
          out.write(open_cv_image)

    count = count + 1

out.release()

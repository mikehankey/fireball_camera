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


# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'H264')
out = cv2.VideoWriter(outfile,fourcc, 25, (640,360),1)

image_list = []
file_list = []
sorted_list = []
for filename in (glob.glob(path + '/*.jpg')): 
    file_list.append(filename)

sorted_list = sorted(file_list)
count = 0
for filename in sorted_list:
    if count % 1 == 0:
       #print (filename)
       open_cv_image = cv2.imread(filename,1)
       height , width, chan =  open_cv_image.shape
       if height > 400:
          open_cv_image = cv2.resize(open_cv_image, (0,0), fx=1, fy=.75)
       #print(open_cv_image.shape)
       #print (height, width)
       #open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
       #equ = cv2.equalizeHist(open_cv_image)
       #rgb_equ = cv2.cvtColor(equ, cv2.COLOR_GRAY2RGB)

       #rgb_equ = cv2.fastNlMeansDenoisingColored(open_cv_image,None,10,10,7,21)
       out.write(open_cv_image)
       #out.write(open_cv_image)

    count = count + 1

out.release()

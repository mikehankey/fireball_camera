#!/usr/bin/python3

from PIL import Image
import cv2
import glob
import sys
import numpy as np
import os
path = sys.argv[1]


# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'H264')
out = cv2.VideoWriter('output.avi',fourcc, 25, (640,480),1)

image_list = []
file_list = []
sorted_list = []
if "time_lapse" not in path:
   print ("error, must be time lapse dir to run this.")
   exit()
for filename in (glob.glob(path + '/*.jpg')): 
    file_list.append(filename)

sorted_list = sorted(file_list)
count = 0
for filename in sorted_list:
    if count % 5 == 0:
       print (filename)
    else:
       cmd = "rm " + filename
       os.system(cmd)
       print (cmd)
   
    count = count + 1

out.release()

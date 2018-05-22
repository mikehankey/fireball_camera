#!/usr/bin/python3

from sklearn.cluster import KMeans
import math
import cv2
import sys
import numpy as np
import glob
from collections import deque
from PIL import Image, ImageChops
import examinelib


dir = sys.argv[1]
cam_num = sys.argv[2]
DEBUG = 0
master_stack_file = dir + "/cam" + str(cam_num) + "-master_stack.jpg"
past_clusters = deque(maxlen=10)
last_cnts = []
hits = 0
stack_files = examinelib.get_stacked_files(dir, cam_num)
new_stack_files, images = examinelib.preload_images(stack_files)
stack_files = new_stack_files
master_stack = None
rpt_file = dir + "/cam" + str(cam_num) + ".txt"
sfp = open(rpt_file, "w")
c = 0
for file in stack_files:
   print(file)
   img = examinelib.median_mask(images, images[c], c)
   last_cnts, cls, hit, status_desc, orig_img = examinelib.examine_still(file, img, last_cnts, past_clusters)
   past_clusters.append(cls)
   hits = hits + hit
   print ("STATUS:", status_desc)
   if hit == 1:
      master_stack = examinelib.stack_stack(orig_img, master_stack)
   data = file + "," + status_desc + "," + str(hit) + "\n"
   sfp.write(data)
   c = c + 1
if master_stack is not None:
   print("saving", master_stack_file)
   master_stack.save(master_stack_file, "JPEG")
print ("Total Files / Total Hits", len(stack_files), hits)

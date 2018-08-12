#!/usr/bin/python3

# script to make master stacks per night and hour from the 1 minute stacks

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import time
from sklearn.cluster import KMeans
from sklearn import datasets

from PIL import Image, ImageChops

from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from random import randint
import time
import ephem
from PIL import Image
import cv2
import glob
import sys
import os
import numpy as np
import datetime
from pathlib import Path
import subprocess
from amscommon import read_config
import math
import time
from sklearn.cluster import Birch
from collections import deque

video_dir = "/mnt/ams2/SD/"

def stack_stack(pic1, pic2):
   if len(pic1.shape) == 3:
      pic1 = cv2.cvtColor(pic1, cv2.COLOR_BGR2GRAY)
   frame_pil = Image.fromarray(pic1)
   stacked_image = pic2
   if pic2 is not None:
      np_stacked_image = np.asarray(stacked_image)

   if stacked_image is None:
      stacked_image = frame_pil
   else:
      stacked_image=ImageChops.lighter(stacked_image,frame_pil)
   return(stacked_image)


def master_stack(cam_num):
   glob_dir = "tmp/" + "*cam" + str(cam_num) + ".jpg"
   stacked_image = None
   for filename in (glob.glob(glob_dir)):
      print (filename)
      frame = cv2.imread(filename,0)
      stacked_image = stack_stack(frame, stacked_image)

   out_file = "tmp/" + "cam" + cam_num + "-all.jpg"
   stacked_image.save(out_file, "JPEG")

def stack_folder():
   glob_dir = "tmp/" + "*.mp4"
   for filename in (glob.glob(glob_dir)):
      jpg_file = filename.replace(".mp4", ".jpg")
      file_exists = Path(jpg_file)
      if (file_exists.is_file()):
         print ("Done already.")
      else:
         cmd = "./stack-full.py " + filename
         os.system(cmd)
         print (cmd)


cam_num = sys.argv[1] 
#stack_folder()
master_stack(cam_num)


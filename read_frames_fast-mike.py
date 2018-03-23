#!/usr/bin/python3 
import numpy as np
from pathlib import Path
import os
import requests
from collections import deque
import multiprocessing
from amscommon import read_config
import datetime
import cv2
import iproc
import time
import syslog
import sys
MORPH_KERNEL = np.ones((10, 10), np.uint8)

def main(orig_video_file):
   pipe_parent, pipe_child = multiprocessing.Pipe()
   man = multiprocessing.Manager()
   shared_dict = man.dict()
   shared_dict['done'] = 0
   cam_process = multiprocessing.Process(target=cam_loop,args=(pipe_parent, shared_dict, orig_video_file))
   cam_process.start()

   show_process = multiprocessing.Process(target=show_loop,args=(pipe_child, shared_dict))
   show_process.start()

   cam_process.join()
   show_loop.join()
   if shared_dict['done'] == 1:
      pipe_child.close()
      pipe_parent.close()
  

def cam_loop(pipe_parent, shared_dict, orig_video_file):
   print("cam", orig_video_file)
   cap = cv2.VideoCapture(orig_video_file)
   fc = 0
   while True:
      _ , frame = cap.read()
      if frame is None:
         print ("done")
         shared_dict['done'] = 1
         #sys.exit(1)
      else:
         print ("FRAME: ", fc)
         pipe_parent.send(frame)
      fc = fc + 1

def show_loop(pipe_child, shared_dict):

   while True:
      frame = pipe_child.recv()
      print("show")


file = sys.argv[1]
main(file)

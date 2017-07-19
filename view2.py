#!/usr/bin/python3
import subprocess
import requests
import pytesseract
from io import BytesIO
from pathlib import Path
import glob
import collections
from collections import deque
from PIL import Image, ImageChops
from queue import Queue
import multiprocessing
import datetime
import cv2
import numpy as np
import iproc
import time
import ephem
import sys
import os
from amscommon import read_config, caldate


def main():
   try:
      file = sys.argv[1]
      batch = 0
   except:
      files = glob.glob("/var/www/html/out/*.avi")
      batch = 1
   try:
      show = sys.argv[2]
   except:
      show = 0

   if batch == 0:
      view(file, show)



def view(file, show):

   dir_name = os.path.dirname(file)
   file_name = file.replace(dir_name + "/", "")
   summary_file_name = file_name.replace(".avi", "-summary.txt")
   data_file_name = file_name.replace(".avi", ".txt")
   screen_cap_file_name = file_name.replace(".avi", ".jpg")
   object_file_name = file_name.replace(".avi", "-objects.jpg")
   capture_date = parse_file_date(file_name)
   #last_cal_date = # Get last / closest calibration date

   print ("Viewing file: " + file)
   print ("Directory: " + dir_name)
   print ("File Name: " + file_name)
   print ("Summary File Name: " + summary_file_name)
   print ("Data File Name: " + data_file_name)
   print ("Screen Cap File Name: " + screen_cap_file_name)
   print ("Object File Name: " + object_file_name)
   print ("Capture Date: " + capture_date)

   # make sure the file exists
   if os.path.isfile(file) is False:
      print("This file does not exist. Exiting.")
      exit()
   else:
      print ("The file is ok.")

   #process video

   tstamp_prev = None
   image_acc = None
   last_frame = None
   nice_image_acc = None
   final_image = None
   cur_image = None
   frame_count = 0

   # open data log file
   fp = open(data_file_name, "w")
   fp.write("frame|contours|x|y|w|h|color|\n")


   #if show == 1:
   #   cv2.namedWindow('pepe') 


   cap = cv2.VideoCapture(file)
   time.sleep(2)
   xs = []
   ys = []
   motion_frames = []
   frames = []

   while True:
      _ , frame = cap.read()
      frame_count = frame_count + 1
      frames.extend([frame])
      if frame is None:
         if frame_count <= 1:
            print("Bad file.")
            exit()
         else:
            print("Processed ", frame_count, "frames.")
            # finish processing file and write output files

            total_motion = len(motion_frames)
            half_motion = int(round(total_motion/2,0))
            print ("key frame #1 : ", 1) 
            print ("key frame #2 : ", half_motion) 
            print ("key frame #3 : ", total_motion -1) 
            print (xs)
            print (ys)
            print (motion_frames)
            object_file_image = (frames[motion_frames[1]] * .33) + (frames[motion_frames[half_motion]] * .33) + (frames[motion_frames[total_motion-1]] * .33) 
           
            x1 = xs[1]
            y1 = xs[1]
            x2 = xs[half_motion]
            y2 = xs[half_motion]
            x3 = xs[total_motion-1]
            y3 = xs[total_motion-1]
            straight_line = compute_straight_line(x1,y1,x2,y2,x3,y3)
            print ("Straight Line:", straight_line)
            obj_outfile = dir_name + "/" + object_file_name
            sc_outfile = dir_name + "/" + screen_cap_file_name 
            cv2.imwrite(obj_outfile, object_file_image)
            #cv2.imwrite(sc_outfile, object_file_image)

            #write summary & data files

            fp.close()
            exit()
      gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      nice_frame = frame

      alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
      frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      frame = cv2.GaussianBlur(frame, (21, 21), 0)
      if last_frame is None:
         last_frame = nice_frame
      if image_acc is None:
         image_acc = np.empty(np.shape(frame))
      image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
      hello = cv2.accumulateWeighted(frame, image_acc, alpha)
      _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
      thresh= cv2.dilate(threshold, None , iterations=2)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      data = str(frame_count) + "|"

      contours = len(cnts)
      x,y,w,h = 0,0,0,0
      if contours > 0:
          x,y,w,h = cv2.boundingRect(cnts[0])
          xs.extend([x])
          ys.extend([y])
          motion_frames.extend([frame_count])
         
      color = 0
      line_data = str(frame_count) + "|" + str(contours) + "|" + str(x) + "|" + str(y) + "|" + str(w) + "|" + str(h) + "|" + str(color) + "|\n"

      fp.write(line_data)
      print (frame_count, contours, x,y,w,h)

      #if frame_count % 2 == 0:
      #  cv2.imshow('pepe', frame)
      #   cv2.waitKey(1) 

   # we will never make it to here cause the program ends when the loop ends. look up.  


def compute_straight_line(x1,y1,x2,y2,x3,y3):
   if x2 - x1 != 0:
      a = (y2 - y1) / (x2 - x1)
   if x3 - x1 != 0:
      b = (y3 - y1) / (x3 - x1)
   straight_line = a - b
   if (straight_line < 1):
      straight = "Y"
   else:
      straight = "N"
   return(straight)

def parse_file_date(file_name):
   year = file_name[0:4]
   month = file_name[4:6]
   day = file_name[6:8]
   hour = file_name[8:10]
   min = file_name[10:12]
   sec = file_name[12:14]
   date_str = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec
   return(date_str)

if __name__ == '__main__':
   main()

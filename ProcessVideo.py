from skimage import morphology
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
import settings
from amscommon import read_config, caldate
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageTk
from PIL import ImageEnhance

class ProcessVideo:
   def __init__(self):
      #self.master = master

      # variables relating to the video file 
      self.orig_video_file = None
      self.stacked_image= None
      self.star_image = None
      self.frame_count = 0
      self.detect_stars = 0
      self.detect_motion = 0
      self.make_stack = 0
      self.star_image_gray = None
      self.star_image_fn = None
      self.report_fn = None
      self.show_video = 0
      self.cam_num = None
      self.capture_date = None
      self.sun_status = None
      self.meteor_yn = None
      self.total_stars = None
      self.starlist = [] 
      self.straight_line = 100
      self.image_stack = []
      self.xs = []
      self.ys = []
      self.colors = []
      self.noise= []
      self.prev_motion= 0
      self.cons_motion= 0
      self.motion= 0
      self.total_motion= 0
      self.motion_events = 0
      self.motion_frames = []
      self.frame_data = []
      self.motion_cnts  = []
      self.file_class = "" # where we will ultiamtely move the file. 
      self.cams = [1,2,3,4,5,6]
      self.file_classes = ['day', 'day_motion', 'day_nomotion', 'night', 'night_motion', 'night_nomotion', 'dist', 'calvid', 'meteor', 'time_lapse']
      self.video_dir = "/home/ams/fireball_camera/ffvids"
      self.config = {}
      self.config_file = "" 

   def chk_dirs(self):
      for dir in self.file_classes:
         dd = self.video_dir + "/" + self.cam_num + "/" + dir
         if not os.path.isdir(dd):
            print("making dir", dd)
            os.mkdir(dd)


   def compute_straight_line(self,x1,y1,x2,y2,x3,y3):
      if x2 - x1 != 0:
         a = (y2 - y1) / (x2 - x1)
      else:
         a = 0
      if x3 - x1 != 0:
         b = (y3 - y1) / (x3 - x1)
      else:
         b = 0
      straight_line = a - b
      if (straight_line < 1):
         straight = "Y"
      else:
         straight = "N"
      return(straight_line)

   def SetCamNum(self, cam_num):
      self.cam_num = cam_num
      self.config_file = "conf/config-" + str(self.cam_num) + ".txt"
      self.config = read_config(self.config_file)

   def move_all_files(self,dest_dir):
      #return(0)
      print (self.orig_video_file, dest_dir)
      if ".avi" in self.orig_video_file:
         wild_card = self.orig_video_file.replace(".avi", "*") 
      else:
         wild_card = self.orig_video_file.replace(".mp4", "*") 
      el = self.orig_video_file.split("/")
      ff = el[-1]
      # copy the time lapse file

      orig_dir = self.orig_video_file.replace(ff, "")
      tl_filename = orig_dir + "time_lapse" + "/" 
      cmd =  "cp " + self.stacked_image_fn + " " + tl_filename
      print(cmd)
      os.system(cmd)

      new_filename = orig_dir + dest_dir + "/" 
      cmd =  "mv " + wild_card + " " + new_filename
      print(cmd)
      os.system(cmd)

   def StackVideo(self):
      sum_image = None
      start_time = int(time.time())
      if self.show_video == 1:
         cv2.namedWindow('pepe')
      self.parse_file_date()
      self.day_or_night()
      if os.path.isfile(self.orig_video_file) is False:
         print("This file does not exist. Exiting.")
         return(0)
      if self.sun_status == 'day':
         print ("Skipping daytime files for now.")
         self.drop_frame()
         self.move_all_files("day")
         mod_skip = 5
      else:
         mod_skip = 3 

      if self.show_video == 1:
         cv2.namedWindow('pepe')

      cap = cv2.VideoCapture(self.orig_video_file)
      while True:
         #cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,frame_count)
         _ , frame = cap.read()
         self.frame_count = self.frame_count + 1

         if frame is None:
            if self.frame_count <= 1:
               cap.release()
               print("Bad file.")
               return(0)
            else:
               end_time = int(time.time())
               elapsed = end_time - start_time
               print("Processed ", self.frame_count, "frames. in ", elapsed, "seconds" )
               cap.release()
               self.cleanup_process()
           
               return(0)

         # main video loop
         if self.frame_count % mod_skip == 0:
            nice_frame_im = Image.fromarray(frame)
            if self.sun_status == 'day':
               if self.stacked_image is None:
                  self.stacked_image = nice_frame_im 
            else:
               if self.stacked_image is None:
                  self.stacked_image = nice_frame_im 
                  self.stacked_image=ImageChops.lighter(self.stacked_image,nice_frame_im)

   def ProcessVideo(self):
      # determine sun status for video
      # play the video frame by frame 
      # detect stars in video
      sum_image = None
      start_time = int(time.time())
      if self.show_video == 1:
         cv2.namedWindow('pepe')


      self.parse_file_date()
      self.day_or_night()
      if os.path.isfile(self.orig_video_file) is False:
         print("This file does not exist. Exiting.")
         return(0)
      #if self.sun_status == 'day':
      #   print("Skip processing on daytime files for now.")
      #   # move file to daytime dir
      #   return(0)
      if self.sun_status == 'day':
         print ("Skipping daytime files for now.")
         self.drop_frame()
         self.move_all_files("day")
         mod_skip = 5
      else:
         mod_skip = 5 

      if self.show == 1:
         cv2.namedWindow('pepe')

      cap = cv2.VideoCapture(self.orig_video_file)

      frame_count = 0
      image_acc = None
      last_frame = None
      nostars = 0
      real_motion = 0
      tstamp_prev = 0
      while True:
         #cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,frame_count)
         _ , frame = cap.read()
         frame_count = frame_count + 1
         self.frame_count = frame_count

         if frame is None:
            if frame_count <= 1:
               cap.release()
               print("Bad file.")
               return(0)
            else:
               end_time = int(time.time())
               elapsed = end_time - start_time
               print("Processed ", frame_count, "frames. in ", elapsed, "seconds" )
               cap.release()
               self.cleanup_process()
           
               return(0)

         # main video loop
         if frame_count % mod_skip == 0:
            # prep up different versions of the frame as needed
            nice_frame = frame
            if self.show_video == 1:
               nice_frame_small = frame
               nice_frame_small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25) 

            nice_frame_im = Image.fromarray(nice_frame)
            #nice_frame_im = Image.fromarray(cleaned)

            # mask out the time for motion detection 
            if self.detect_motion == 1:
               if frame is not None:
                  masked = frame[680:720, 0:620] 
                  frame[680:720, 0:620] = [0,0,0]

               frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
               frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
               frame = cv2.GaussianBlur(frame, (21, 21), 0) 
        
               # setup image accumulation 
               if last_frame is None:
                  last_frame = nice_frame
               if image_acc is None:
                  image_acc = np.empty(np.shape(frame))

               image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
               alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
               hello = cv2.accumulateWeighted(frame, image_acc, alpha)
               _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
               thresh= cv2.dilate(threshold, None , iterations=2)
               (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
               #print("CNTS:", len(cnts))
               real_cnts = []
               if len(cnts) > 0:
                  for (i,c) in enumerate(cnts):
                     x,y,w,h = cv2.boundingRect(cnts[i])
                     if w > 5 and h > 5 and frame_count > 8:
                        real_cnts.append([x,y,w,h])
                        self.motion_cnts.append([frame_count,len(cnts),x,y,w,h])
               if len(real_cnts) >= 1:
                  self.total_motion = self.total_motion + 1
                  self.xs.append(x)
                  self.ys.append(y)
                  self.frame_data.append([frame_count, len(real_cnts),x,y,w,h])
                  if self.prev_motion == 1:
                     self.cons_motion = self.cons_motion + 1
                  else:
                     self.motion_events = self.motion_events + 1
                  if self.motion == 1:
                     self.prev_motion = 1
                  else:
                     self.prev_motion = 0
                  self.motion = 1
                  self.motion_frames.append(frame_count)
               else:
                  real_cnts = []
                  self.frame_data.append([frame_count, len(real_cnts),0,0,0,0])
                  #print ("no motion", frame_count, 0,0,0, 0,0)
                  #print ("No real motion")


            if self.make_stack != 0:
               # stacked the video into a single frame
               if self.sun_status == 'day':
                  if self.stacked_image is None:
                     self.stacked_image = nice_frame_im 

               else:
                  if self.stacked_image is None:
                     self.stacked_image = nice_frame_im 
                  self.stacked_image=ImageChops.lighter(self.stacked_image,nice_frame_im)

            

            #if frame_count > 50 and self.total_stars == 0:
            #   # too cloudy to see anything move on. 
            #   cap.release()
       
               

            if self.detect_stars == 1:
               # check to see if the image has stars in it. 
               # if no images exist it is cloudy and we should abort. 
               if 5 < frame_count < 50 and self.sun_status != 'day':

                  if self.star_image is None:
                     self.star_image = nice_frame_im 
                     self.star_image=ImageChops.lighter(self.star_image,nice_frame_im)
                  self.image_stack.append(nice_frame)
                  median = np.median(np.array(self.image_stack), axis=0)
                  median = np.uint8(median)
                  med_gray = cv2.cvtColor(median, cv2.COLOR_BGR2GRAY)

   
                  median_im = Image.fromarray(median)
                  if frame_count % 5 == 0:
                     self.star_image=ImageChops.lighter(self.star_image,median_im)
                     self.image_stack = []

                  np_star_image = np.asarray(self.star_image)
                  np_star_image_gray = cv2.cvtColor(np_star_image, cv2.COLOR_BGR2GRAY)

          
                  self.total_stars, self.star_image_gray = self.find_stars(np_star_image_gray)
                  #total_stars, star_image = self.find_stars(cleaned)
                  if self.total_stars == 0:
                     print("Cloudy...???")
                     nostars = nostars + 1
                  else:
                     nostars = 0
            if self.show_video == 1:
               if 5 < frame_count < 50 and self.sun_status != 'day':
                  if self.detect_stars == 1: 
                     star_image_small = cv2.resize(np.asarray(self.star_image_gray), (0,0), fx=0.5, fy=0.5) 
                  else:
                     star_image_small = frame
                  cv2.imshow('pepe', star_image_small)
                  cv2.waitKey(1)
               else:
                  np_stacked_image = np.asarray(self.stacked_image)
                  with_stars = self.draw_stars(np_stacked_image)
                  stacked_image_small = cv2.resize(with_stars, (0,0), fx=0.5, fy=0.5) 
                  cv2.imshow('pepe', stacked_image_small)
                  cv2.waitKey(1)

   def draw_stars(self, img):
      for (x,y,w,h,avg_flux,max_flux,total_flux) in self.starlist:
         cv2.circle(img, (x,y), 10, (255,0,0), 1)
      return(img)

   def drop_frame(self):
      cap = cv2.VideoCapture(self.orig_video_file)
      _ , frame = cap.read()
      cv2.imwrite(self.stacked_image_fn, frame)
      cap.release()

   def cleanup_process(self):
      #print ("yo")
      xl = len(self.xs)
      yl = len(self.ys)
      if xl >= 3 :
         sf = 0 
         mf = int(xl/2)
         ef = xl - 1
         self.straight_line = self.compute_straight_line(self.xs[sf],self.ys[sf],self.xs[mf],self.ys[mf],self.xs[ef],self.ys[ef])

         #print ("Straight Line:", self.straight_line)
     
         if self.straight_line >= -0.9 and self.straight_line < 1:
            self.meteor_yn = "Y"
         else:
            self.meteor_yn = "N"
     
 
          
      np_stacked_image = np.asarray(self.stacked_image)
      np_star_image = np.asarray(self.star_image_gray)
      #cleaned_stack = morphology.remove_small_objects(np_stacked_image, min_size=2, connectivity=12)
      cleaned_stack = cv2.fastNlMeansDenoisingColored(np_stacked_image,None,8,8,7,21)
      #cleaned_stars = cv2.fastNlMeansDenoising(np_star_image,None,8,8,7,21)

      #cv2.imwrite(self.stacked_image_fn, np_stacked_image)
      if self.sun_status != 'day' and self.detect_stars == 1: 
         print ("Writing:", self.star_image_fn)
         cv2.imwrite(self.star_image_fn, np_star_image)
      #cv2.imwrite(self.star_image_fn, cleaned_stars)
      print ("Writing:", self.stacked_image_fn)
      cv2.imwrite(self.stacked_image_fn, cleaned_stack)
      report = "File:" + self.orig_video_file + "\n"
      report = report + "Total Frames:" + str(self.frame_count) + "\n"
      report = report + "FPS:" + str(self.frame_count/60) + "\n"
      report = report + "Sun Status:" + self.sun_status + "\n"
      report = report + "Total Stars:" + str(self.total_stars) + "\n"
      report = report + "Star List:" + str(self.starlist) + "\n"
      report = report + "Total Motion:" + str(self.total_motion) + "\n"
      if self.total_motion >= 1:
         report = report + "Motion Frames:" + str(self.motion_frames) + "\n"
         report = report + "Contours:" + str(self.motion_cnts) + "\n"
         report = report + "Straight Line:" + str(self.straight_line) + "\n"
         report = report + "Meteor Y/N:" + str(self.meteor_yn) + "\n"
         report = report + "Cons Motion Events:" + str(self.motion_events) + "\n"
         #print("Contours :" + self.motion_cnts)
         #for (frame_count,cn,x,y,w,h) in self.frame_data:
         #   report = report + str(frame_count) + "," + str(cn) + "," + str(x) + "," + str(y) + "," + str(w) + "," + str(h) + "\n"
      # Write out report file.
      #print ("Writing: ", self.report_fn)
      #fp = open(self.report_fn, "w")
      #fp.write(report)
      #fp.close()
      #print (report)


      #self.file_classes = ['day', 'day_motion', 'day_nomotion', 'night', 'night_motion', 'night_nomotion', 'dist', 'calvid', 'meteor']
      if self.meteor_yn == "Y":
         print ("Meteor Detected!")
         # Move all files to meteor dir
         self.move_all_files("meteor")

      elif self.total_motion >= 2:
         print ("Some motion but not a meteor!")
         # move all files to day or night motion dir 
         if self.sun_status == 'day':
            self.move_all_files("day_motion")
         else:
            self.move_all_files("night_motion")

      else:
         print ("No motion detected.")
         if self.sun_status == 'day':
            self.move_all_files("day_nomotion")
         else:
            self.move_all_files("night_nomotion")
         #move file to non motion dir
         # move all files to day or night no motion dir 


 
   def find_stars(self, star_image):
      star_image.setflags(write=1)
      star_image[680:720, 0:620] = [0]

      # find stars
      total_stars = 0
      star_image_gray = star_image

      cloudy = 0

      avg_px = np.average(star_image_gray)
      ax_pixel = np.amax(star_image_gray)
      bp_dif = ax_pixel - avg_px
      lower_thresh = avg_px + (bp_dif / 2)
      print ("Sky info:", avg_px, ax_pixel, ax_pixel / avg_px)
      if ax_pixel / avg_px < 3:
         print ("there are no stars, likely cloudy... should skip.")
         total_stars = 0
         cloudy = 1
      else:
         #lower_thresh = avg_px * 3
         #star_image_gray = cv2.GaussianBlur(star_image_gray, (1, 1), 0)
         _, nice_threshold = cv2.threshold(star_image_gray, lower_thresh, 255, cv2.THRESH_BINARY)
         (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         contours = len(cnts)
         size=6
         print("CNTS:", contours)
         if contours > 100:
            lower_thresh = avg_px + (bp_dif / 2)
            _, nice_threshold = cv2.threshold(star_image_gray, lower_thresh, 255, cv2.THRESH_BINARY)
            (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = len(cnts)

         #print ("Cloudy:", cloudy)
         #total_stars = contours
         #print ("Total Stars: ", total_stars)
         if contours > 0 and cloudy == 0:
            self.starlist = []
            for (i,c) in enumerate(cnts):
               x,y,w,h = cv2.boundingRect(cnts[i])
               avg_flux, max_flux, total_flux, ox,oy = self.find_flux(x,y,size,star_image_gray)
               #print ("OXOY:", ox, oy)
               #print ("FLUX:", i, w, h, avg_flux, max_flux, total_flux)
               #x = x - ox
               #y = y - oy
               if avg_flux > 0:
                  ff = max_flux / avg_flux
               else:
                  avg_flux = 1
               if max_flux > 10 and (w < 10 and h < 10) and ff > 1.1:
                  #print ("Passed flux test")
                  #cv2.circle(star_image_gray, (x,y), 10, (255), 1)
                  cv2.circle(star_image_gray, (x+ox,y+oy), 10, (255), 1)
                  tag = str(ox) + "," + str(oy)
                  #cv2.putText(star_image_gray, tag, (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)


                  total_stars = total_stars + 1
                  self.starlist.append([x+ox,y+oy,w,h,avg_flux,max_flux,total_flux])
               else:
                  #print ("Failed flux test", w,h, max_flux, ff)
                  cv2.circle(star_image_gray, (x,y), 20, (120), 1)
                  #total_stars = total_stars + 1
      return(total_stars, star_image_gray)


   def find_flux(self, x,y,size,image):
      #cv2.imshow('pepe', image)
      #cv2.waitKey(2000)
      box = (x-size,y-size,x+size,y+size)
      #print ("BOX", box)
      new_image = Image.fromarray(image)

      flux_box = new_image.crop(box)


      flux_box_show = flux_box.resize((75,75), Image.ANTIALIAS)
      gray_flux_box = flux_box.convert('L')
      np_flux_box = np.asarray(gray_flux_box)



      #is there a circle shape in the center of this box?
      #if circles is None:
      #   return(0,0,0,0,0) 
      #else:
      #   print(circles)


      offw= int(np_flux_box.shape[1] / 2)
      offh = int(np_flux_box.shape[0] / 2)


      np_flux_box = cv2.GaussianBlur(np_flux_box, (21, 21), 0)
      avg_flux = np.average(np_flux_box)
      max_flux = np.amax(np_flux_box)
      bp_diff = max_flux - avg_flux
      lower_thresh = avg_flux + (bp_diff / 2)

      ffw= int(np_flux_box.shape[1] / 2)
      ffh = int(np_flux_box.shape[0] / 2)

      total_flux = np.sum(np_flux_box)
      #print("FLUX", int(avg_flux), int(max_flux), int(total_flux))
      #return (int(avg_flux), int(max_flux), int(total_flux))

      #is the x,y passed in actually the brightest center point? 
      abr = 0
      for afx in range(0,np_flux_box.shape[1]):
         for afy in range(np_flux_box.shape[0]):
            pixel_val = np_flux_box[afx,afy]
            if pixel_val > abr:
               #print ("Brightest Pixel Value", afx, afy, pixel_val)
               brightest_pix = (afx,afy)
               abr = pixel_val
      if abr == 0:
         brightest_pix = (ffw,ffh)

      (cxx,cxy) = brightest_pix

      #circles = cv2.HoughCircles(np_flux_box,cv2.HOUGH_GRADIENT,1,120,
      #                     param1=100,param2=30,minRadius=0,maxRadius=0)
      #if circles is not None:
      #   print(circles)

      tag = str(x) + "," + str(y) + "/ " + str(cxx) + "," + str(cxy)
      ox = int((cxx - offw) )
      oy = int((cxy - offh) )
      #print("Center Flux Box is:", ffw,ffh)
      #print("CNT Center:", cxx,cxy)
      #print("Offset :", ox,oy)

      new_x = x+ox
      new_y = y+oy
      #print("X,Y,OX,OY,NX,XY", x,y,ox,oy,new_x,new_y) 
      np_flux_box_tiny = image[new_y-5:new_y+5, new_x-5:new_x+5]
      total_flux = np.sum(np_flux_box_tiny)
      np_flux_box.setflags(write=1)


      #cv2.circle(np_flux_box, (ffw,ffh), 3, (120), 1)
      #cv2.circle(np_flux_box, (cxx,cxy), 7, (255), 1)
      #cv2.circle(np_flux_box, (cxx-ox,cxy-oy), 12, (255), 1)
      if np_flux_box_tiny.shape[0] > 0 and np_flux_box_tiny.shape[1] > 0:


         np_flux_box_tiny_show = cv2.resize(np_flux_box_tiny, (0,0), fx=20, fy=20) 
         _, threshold = cv2.threshold(np_flux_box_tiny_show, lower_thresh, 255, cv2.THRESH_BINARY)
         np_flux_box_tiny_show = threshold

         #print(np_flux_box_tiny_show.shape[0], np_flux_box_tiny_show.shape[1])
         #kernel = (np.array([[-1, -1, -1],
         #           [-1,  9, -1],
         #           [-1, -1, -1]]))
         #filtered = cv2.filter2D(src=np_flux_box_tiny_show, kernel=kernel, ddepth=-1)

         params = cv2.SimpleBlobDetector_Params()
         params.minThreshold = 50
         params.maxThreshold = 255
         params.filterByArea= True 
         params.minArea = 100
         params.maxArea = 10000
         #params.filterByCircularity = True
         #params.minCircularity = .8
         params.filterByConvexity = True
         params.minConvexity = .87
         params.filterByColor=False

         detector = cv2.SimpleBlobDetector_create(params)
         keypoints = detector.detect(np_flux_box_tiny_show)
         #print("Keypoints:", keypoints)
         im_with_keypoints = cv2.drawKeypoints(np_flux_box_tiny_show, keypoints, np.array([]), (255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

         #cv2.imshow('pepe', im_with_keypoints)
         #cv2.waitKey(1000)
         #cv2.imshow('pepe', np_flux_box_tiny_show)
         #cv2.waitKey(1000)

         if keypoints is None:
            return(int(0), int(0), int(0), ox, oy)
         else:
            #print("FLX PASS:", avg_flux, max_flux, total_flux) 
            return(int(avg_flux), int(max_flux), int(total_flux), ox, oy)
      else:
         return(int(0), int(0), int(0), ox, oy)
 


   def day_or_night(self):

      obs = ephem.Observer()

      obs.pressure = 0
      obs.horizon = '-0:34'
      obs.lat = self.config['device_lat']
      obs.lon = self.config['device_lng']
      obs.date = self.capture_date 

      sun = ephem.Sun()
      sun.compute(obs)

      (sun_alt, x,y) = str(sun.alt).split(":")

      saz = str(sun.az)
      (sun_az, x,y) = saz.split(":")
      print ("SUN", sun_alt)
      if int(sun_alt) < -1:
         self.sun_status = "night"
      else:
         self.sun_status = "day"

   def parse_file_date(self):
      print(self.orig_video_file)
      if ".mp4" in self.orig_video_file:
         self.stacked_image_fn = self.orig_video_file.replace(".mp4", "-stack.jpg") 
         self.star_image_fn = self.orig_video_file.replace(".mp4", "-stars.jpg") 
         self.report_fn = self.orig_video_file.replace(".mp4", "-report.txt") 
      else:
         self.stacked_image_fn = self.orig_video_file.replace(".avi", "-stack.jpg") 
         self.star_image_fn = self.orig_video_file.replace(".avi", "-stars.jpg") 
         self.report_fn = self.orig_video_file.replace(".avi", "-report.txt") 
      el = self.orig_video_file.split("/") 
      file_name = el[-1]
      cam_num = el[-2]
      self.SetCamNum(cam_num)
      self.chk_dirs() 
      print ("VID: ", self.orig_video_file)
      print ("STAR IMG: ", self.star_image_fn)
      print ("STACK IMG: ", self.stacked_image_fn)
    
      file_name = file_name.replace("capture-", "")
      file_name = file_name.replace("-", "")
      file_name = file_name.replace("_", "")
      year = file_name[0:4]
      month = file_name[4:6]
      day = file_name[6:8]
      hour = file_name[8:10]
      min = file_name[10:12]
      sec = file_name[12:14]
      date_str = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec
      self.capture_date = date_str


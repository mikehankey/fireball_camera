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
      self.stacked_image_fn = None
      self.star_image = None
      self.star_image_gray = None
      self.star_image_fn = None
      self.report_fn = None
      self.show_video = 0
      self.cam_num = None
      self.capture_date = None
      self.sun_status = None
      self.meteor_yn = None
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
      self.file_classes = ['day', 'day_motion', 'day_nomotion', 'night', 'night_motion', 'night_nomotion', 'dist', 'calvid', 'meteor']
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
      print (self.orig_video_file, dest_dir)
      if ".avi" in self.orig_video_file:
         wild_card = self.orig_video_file.replace(".avi", ".*") 
      else:
         wild_card = self.orig_video_file.replace(".mp4", ".*") 
      el = self.orig_video_file.split("/")
      ff = el[-1]
      new_filename = self.orig_video_file.replace(ff, "")
      new_filename = new_filename + dest_dir + "/" 
      cmd =  "mv " + wild_card + " " + new_filename
      print(cmd)
      #os.system(cmd)


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
         mod_skip = 25 
      else:
         mod_skip = 5 

      self.show = 1
      if self.show == 1:
         cv2.namedWindow('pepe')

      cap = cv2.VideoCapture(self.orig_video_file)
      time.sleep(2)

      frame_count = 0
      image_acc = None
      last_frame = None
      nostars = 0
      real_motion = 0
      tstamp_prev = 0
      while True:
         _ , frame = cap.read()
         frame_count = frame_count + 1

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
            nice_frame_small = frame
            nice_frame_small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 

            nice_frame_im = Image.fromarray(nice_frame)
            #nice_frame_im = Image.fromarray(cleaned)

            # mask out the time for motion detection 
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
            #alpha = .1
            alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
            hello = cv2.accumulateWeighted(frame, image_acc, alpha)
            _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
            thresh= cv2.dilate(threshold, None , iterations=2)
            (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print("CNTS:", len(cnts))
            real_cnts = []
            if len(cnts) > 0:
               for (i,c) in enumerate(cnts):
                  x,y,w,h = cv2.boundingRect(cnts[i])
                  #avg_flux, max_flux, total_flux, ox,oy = self.find_flux(x,y,w,star_image_gray)
                  if w > 5 and h > 5 and frame_count > 8:
                     cv2.rectangle(frame, (x,y), (x+w, y+h), (255),2)
                     real_cnts.append([x,y,w,h])
                     self.motion_cnts.append([frame_count,len(cnts),x,y,w,h])
                  #else:
                  #   print ("not real motion")

            if len(real_cnts) >= 1:
               self.total_motion = self.total_motion + 1
               print ("motion", frame_count, x,y, w,h)
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
               print ("no motion", frame_count, 0,0,0, 0,0)
               #print ("No real motion")



            # stacked the video into a single frame
            if self.sun_status == 'Day':
               if self.stacked_image is None:
                  self.stacked_image = nice_frame_im 

            else:
               if self.stacked_image is None:
                  self.stacked_image = nice_frame_im 
               self.stacked_image=ImageChops.lighter(self.stacked_image,nice_frame_im)

            


            # check to see if the image has stars in it. 
            # if no images exist it is cloudy and we should abort. 
            if 5 < frame_count < 50 and self.sun_status != 'day':

               if self.star_image is None:
                  self.star_image = nice_frame_im 
                  self.star_image=ImageChops.lighter(self.star_image,nice_frame_im)
               self.image_stack.append(nice_frame)
               #print(self.star_image)
               median = np.median(np.array(self.image_stack), axis=0)
               median = np.uint8(median)
               med_gray = cv2.cvtColor(median, cv2.COLOR_BGR2GRAY)
               #print(med_gray.shape)

   
               median_im = Image.fromarray(median)
               #median_im = Image.fromarray(med_gray)
               #print(self.star_image)
               #print(median_im)
               if frame_count % 5 == 0:
                  self.star_image=ImageChops.lighter(self.star_image,median_im)
                  self.image_stack = []

               np_star_image = np.asarray(self.star_image)
               np_star_image_gray = cv2.cvtColor(np_star_image, cv2.COLOR_BGR2GRAY)
               gray_nice_frame = cv2.cvtColor(nice_frame_small, cv2.COLOR_BGR2GRAY)

          
               total_stars, self.star_image_gray = self.find_stars(np_star_image_gray)
               #total_stars, star_image = self.find_stars(cleaned)
               if total_stars == 0:
                  print("Cloudy...???")
                  nostars = nostars + 1
               else:
                  nostars = 0
            if self.show_video == 1:
               if 5 < frame_count < 50:
                  
                  star_image_small = cv2.resize(np.asarray(self.star_image_gray), (0,0), fx=0.5, fy=0.5) 
                  #cv2.imshow('pepe', star_image_small)
                  cv2.imshow('pepe', frame)
                  #cv2.imshow('pepe', thresh)
                  #cv2.imshow('pepe', image_diff)
                  #cv2.imshow('pepe', cv2.convertScaleAbs(image_acc))
                  cv2.waitKey(1)
               else:
                  np_stacked_image = np.asarray(self.stacked_image)
                  stacked_image_small = cv2.resize(np_stacked_image, (0,0), fx=0.5, fy=0.5) 
                  #cv2.imshow('pepe', stacked_image_small)
                  cv2.imshow('pepe', frame)
                  #cv2.imshow('pepe', thres)
                  #cv2.imshow('pepe', image_diff)
                  #cv2.imshow('pepe', cv2.convertScaleAbs(image_acc))
                  cv2.waitKey(1)


   def cleanup_process(self):
      #print ("yo")
      xl = len(self.xs)
      yl = len(self.ys)
      if xl >= 3 :
         sf = 0 
         mf = int(xl/2)
         ef = xl - 1
         self.straight_line = self.compute_straight_line(self.xs[sf],self.ys[sf],self.xs[mf],self.ys[mf],self.xs[ef],self.ys[ef])

         print ("Straight Line:", self.straight_line)
     
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
      if self.sun_status != 'day': 
         print ("Writing:", self.star_image_fn)
         cv2.imwrite(self.star_image_fn, np_star_image)
      #cv2.imwrite(self.star_image_fn, cleaned_stars)
      print ("Writing:", self.stacked_image_fn)
      cv2.imwrite(self.stacked_image_fn, cleaned_stack)

      print("File:", self.orig_video_file)
      print("Total Motion:", self.total_motion)
      if self.total_motion >= 1:
         print("Motion Frames:", self.motion_frames)
         print("Meteor Y/N:", self.meteor_yn)
         print("Cons Motion Events:", self.motion_events)
         #print("Contours :", self.motion_cnts)
         for (frame_count,cn,x,y,w,h) in self.frame_data:
            print (frame_count,cn,x,y,w,h) 
         # Write out report file.


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
      lower_thresh = avg_px + (bp_dif / 3)
      if avg_px * 2 > ax_pixel or ax_pixel < 30:
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
         #print ("Cloudy:", cloudy)
         total_stars = contours
         #print ("Total Stars: ", total_stars)
         if contours > 0 and cloudy == 0:
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
               if max_flux > 30 and (w < 8 and h < 8) and ff > 2:
                  #print ("Passed flux test")
                  #cv2.circle(star_image_gray, (x,y), 10, (255), 1)
                  cv2.circle(star_image_gray, (x+ox,y+oy), 10, (255), 1)
                  tag = str(ox) + "," + str(oy)
                  #cv2.putText(star_image_gray, tag, (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)


                  total_stars = total_stars + 1
               else:
                  #print ("Failed flux test", w,h, max_flux, ff)
                  cv2.circle(star_image_gray, (x,y), 20, (120), 1)
                  #total_stars = total_stars + 1
      return(total_stars, star_image_gray)


   def find_flux(self, x,y,size,image):
      box = (x-size,y-size,x+size,y+size)
      #print ("BOX", box)
      new_image = Image.fromarray(image)

      flux_box = new_image.crop(box)


      #flux_box = flux_box.resize((75,75), Image.ANTIALIAS)
      gray_flux_box = flux_box.convert('L')

      np_flux_box = np.asarray(gray_flux_box)
      offw= int(np_flux_box.shape[1] / 2)
      offh = int(np_flux_box.shape[0] / 2)


      #np_flux_box = cv2.GaussianBlur(np_flux_box, (21, 21), 0)
      avg_flux = np.average(np_flux_box)
      max_flux = np.amax(np_flux_box)

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
      box_tiny = (cxx-1,cxy-1,cxx+1,cxy+1)
      np_flux_box_tiny = np_flux_box[cxy-1:cxy+1, cxx-1:cxx+1]
      total_flux = np.sum(np_flux_box_tiny)
      np_flux_box.setflags(write=1)
      tag = str(x) + "," + str(y) + "/ " + str(cxx) + "," + str(cxy)
      ox = int((cxx - offw) )
      oy = int((cxy - offh) )
      #print("Center Flux Box is:", ffw,ffh)
      #print("CNT Center:", cxx,cxy)
      #print("Offset :", ox,oy)

      #cv2.circle(np_flux_box, (ffw,ffh), 3, (120), 1)
      #cv2.circle(np_flux_box, (cxx,cxy), 7, (255), 1)
      #cv2.circle(np_flux_box, (cxx-ox,cxy-oy), 12, (255), 1)

      #cv2.imshow('pepe', np_flux_box)
      #cv2.waitKey(1)

      return(int(avg_flux), int(max_flux), int(total_flux), ox, oy)
 


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

      if int(sun_alt) < -5:
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


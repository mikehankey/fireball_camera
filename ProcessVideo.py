from random import randint
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
import math 
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
      self.image_acc = None
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
      self.points = []
      self.colors = []
      self.noise= []
      self.cx= 0
      self.cy= 0
      self.max_x= 0
      self.max_y= 0
      self.min_x= 0
      self.min_y= 0
      self.prev_motion= 0
      self.cons_motion= 1
      self.motion= 0
      self.total_motion= 0
      self.motion_events = 0
      self.motion_frames = []
      self.frames = []
      self.frame_data = []
      self.motion_cnts  = []
      self.file_class = "" # where we will ultiamtely move the file. 
      self.cams = [1,2,3,4,5,6]
      self.file_classes = ['day', 'day_motion', 'day_nomotion', 'night', 'night_motion', 'night_nomotion', 'dist', 'calvid', 'meteor', 'time_lapse']
      self.video_dir = "/mnt/ams2/SD"
      self.video_dir_hd = "/mnt/ams2/HD"
      self.config = {}
      self.config_file = "" 

   def ls_HD(self, hd_date, cam_num):
      xyear = hd_date.strftime("%Y")
      xmon = hd_date.strftime("%m")
      xday = hd_date.strftime("%d")
      xhour = hd_date.strftime("%H")
      xmin = hd_date.strftime("%M")

      hd_str = self.video_dir_hd + "/" + str(xyear) + "-" + str(xmon) + "-" + str(xday) + "_" + str(xhour) + "-" +str(xmin) + "*cam" + cam_num + "*"
      cmd = "ls " + hd_str
      output = subprocess.check_output(cmd, shell=True).decode("utf-8")
      files = output.split("\n")
      return(files[0])

   def find_HD_files(self, start_frame = 0):

      (cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = self.parse_date(self.orig_video_file)
      hd_str = self.video_dir_hd + "/" + str(xyear) + "-" + str(xmonth) + "-" + str(xday) + "_" + str(xhour) + "-" +str(xmin) + "*cam" + cam_num + "*"
      cmd = "ls " + hd_str
      print (cmd)
      output = subprocess.check_output(cmd, shell=True).decode("utf-8")
      files = output.split("\n")
      print(files)
      (hcam_num, hdate_str, hyear, hmonth, hday, hhour, hmin, hsec) = self.parse_date(files[0])
      sd_date = datetime.datetime(int(xyear),int(xmonth),int(xday),int(xhour),int(xmin),int(xsec)) 
      hd_date = datetime.datetime(int(hyear),int(hmonth),int(hday),int(hhour),int(hmin),int(hsec)) 
      td = (sd_date - hd_date).total_seconds()
      print("SD/HD offset", xsec, hsec, td)
      print("The HD file started ", td, "seconds before the SD file." )
      print("So if you want to find what you're looking ")
      print ("check the HD file for this same minute and ALSO the file")
      if td > 1:
         print("BEFORE this minute") 
         offset_hd_date = hd_date - datetime.timedelta(seconds=td)
         offset_hd_date_end = offset_hd_date + datetime.timedelta(seconds=60)
         print("the start hd date is", offset_hd_date)
         print("the end hd date is", offset_hd_date_end)
         HD_file1 = self.ls_HD(offset_hd_date, self.cam_num)
         HD_file2 = self.ls_HD(offset_hd_date_end, self.cam_num)
         print(HD_file1, HD_file2)
         hd_cat_file = HD_file1.replace(".mp4", "-cat.mp4")
         cmd = "ffmpeg -i \"concat:" + HD_file1 + "|" + HD_file2 + "\" -c copy " + hd_cat_file
         print(cmd)
         output = subprocess.check_output(cmd, shell=True).decode("utf-8")
         print("MADE:", hd_cat_file)
     

   def load_report(self):
      file_exists = Path(self.report_fn)
      if (file_exists.is_file()):
         print("File found.")
      else:
         print("File not found.") 
         return(0)
      fp = open(self.report_fn, "r")
      for lines in fp:
         line, jk = lines.split("\n")
         field, val = line.split("=")
         exec("self."+line)
      fp.close()
      return(1)

   def chk_dirs(self):
      for dir in self.file_classes:
         dd = self.video_dir + "/" + self.cam_num + "/" + dir
         if not os.path.isdir(dd):
            os.mkdir(dd)

   def examine_cnts(self):
      gc = 1 
      real_groups = 0
      for cnt_group in self.event_cnts:
         print ("Contour Group:", gc)
         rc = 0
         if len(cnt_group) >3:
            for (frame_count,tot_cnts,x,y,w,h) in cnt_group:
               if tot_cnts > 1:
                  print ("there are too many cnts in this frame, skip")

               else:
                  print ("CG:", frame_count, tot_cnts, x,y,w,h)
                  rc = rc + 1
         else:
            print("group too small, skipping.")
         if rc < 4:
            print ("There are not enough 'real' contours in this group.")
         else:
            print ("Maybe this is a real group, we can eval further")
            real_groups = real_groups + 1
         gc = gc + 1
         return(real_groups)
      

   def is_straight(self, points):
      last_angle = None
      total = len(points)
      print ("TP", total)
      passed = 0
      for i in range(1,total):
         print(i)
         angle = self.find_angle(points[0][0], points[0][1], points[i][0], points[i][1])
         print (points[0][0], points[0][1], points[i][0], points[i][1], angle)
         if last_angle is not None:
            if (last_angle - 1) < angle < (last_angle + 1):
               passed = passed + 1
               print("passed")
            else:
               print("failed")

         last_angle = angle

      match_percent = passed / (total - 2)
      if match_percent > .6:
         return(1) 
      else:
         return(0) 

   def find_angle(self, x1,x2,y1,y2):
      if x2 - x1 != 0:
         a1 = (y2 - y1) / (x2 - x1)
      else:
         a1 = 0
      angle = math.atan(a1)
      angle = math.degrees(angle)

      return(angle)

   def calc_dist(self, x1,y1,x2,y2):
      dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
      return dist

   def find_objects(self,index, points):
      apoints = []
      sorted_points = []
      last_angle = None
      objects = []
      group_pts = []
      count = 0
      x1,y1 = points[index-count]
      for x1,y1 in points:
         for x2,y2 in points:
            dist = self.calc_dist(x1,y1,x2,y2)
            angle = self.find_angle(x1,y1,x2,y2)
            if dist > 10 and dist < 100:
               apoints.append((dist,angle,(x1,y1),(x2,y2)))
            count = count + 1
      sorted_points = sorted(apoints, key=lambda x: x[1])

      for dist,angle,(x1,y1),(x2,y2) in sorted_points:
         if last_angle != None:
            if ((last_angle - 5) < angle < (last_angle + 5)) and (dist > 5 and dist < 70):
               group_pts.append((dist,angle,(x1,y1),(x2,y2)))
            #  print ("MATCHING POINTS DX/AN", dist, angle, x1,y1,x2,y2)
            else:
               if len(group_pts) >= 3:
                  #print("NEW GROUP")
                  objects.append(group_pts)
                  group_pts = []
               else:
                  group_pts = []
         last_angle = angle
      if len(group_pts) >= 3:
         objects.append(group_pts)
      return(objects)

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
      return(0)
      if "HD" in self.orig_video_file:
         print ("HD FILE!")

         for event in self.motion_frames:
            if len(event) > 3:
               start = int(event[0]) - 50
               cmd = "./trim_video.py " + self.orig_video_file + " " + str(event[0] - 50) + " " + str( event[-1]+50)
               print (cmd)
               os.system(cmd)
               self.xs = []
               self.ys = []
               for frame_num in event:
                  for frame_count,tot_cnt,x,y,w,h in self.motion_cnts:
                     print ("COMPARE: ", frame_num, frame_count)
                     if int(frame_num) == int(frame_count):
                        print ("ADD X,Ys")
                        self.xs.append(x)
                        self.ys.append(y)
               self.start_frame = event[0] - 50
               print("XSYS", self.xs, self.ys)
               self.trim_file = self.orig_video_file.replace(".mp4", "-trim-" + str(start) + ".mp4")
               self.cropVideo()
         #cmd = "./PV.py crop " + str(self.orig_video_file)
         #os.system(cmd)
         exit()
      if ".avi" in self.orig_video_file:
         wild_card = self.orig_video_file.replace(".avi", "*") 
      else:
         wild_card = self.orig_video_file.replace(".mp4", "*") 
      el = self.orig_video_file.split("/")
      ff = el[-1]

      if dest_dir == "meteor":
         print ("TRIM: ", self.motion_frames[0] - 25, self.motion_frames[-1]+25)
         #self.trimVideo(self.motion_frames[0] - 25, self.motion_frames[-1]+25)
         cmd = "./trim_video.py " + self.orig_video_file + " " + str(self.motion_frames[0] - 50) + " " + str( self.motion_frames[-1]+50)
         #print (cmd)
         #os.system(cmd)


      # copy the time lapse file

      orig_dir = self.orig_video_file.replace(ff, "")
      tl_filename = orig_dir + self.cam_num + "/time_lapse" + "/" 
      latest_filename = "/var/www/html/out/latest" + self.cam_num + ".jpg" 
      cmd =  "cp " + self.stacked_image_fn + " " + tl_filename
      os.system(cmd)
      cmd =  "cp " + self.stacked_image_fn + " " + latest_filename 
      os.system(cmd)

      new_filename = orig_dir + self.cam_num + "/" + dest_dir + "/" 
      cmd =  "mv " + wild_card + " " + new_filename
      #print(cmd)
      os.system(cmd)

   def find_HD_video(self, start, end):
      self.parse_file_date()
      self.day_or_night()

      self.HD_orig_video_file = self.orig_video_file.replace("SD", "HD") 
      el = self.HD_orig_video_file.split("/")
      file_name = el[-1]
      hd_video_dir = "/mnt/ams2/HD/"
      
      (dd,tt) = self.capture_date.split(" ")
      (yr,mm,da) = dd.split("-")
      (h,m,s) = tt.split(":")
      hd_wildcard = hd_video_dir + dd + "_" + h + "-" + m + "*cam" + self.cam_num + "*.mp4"
      files = glob.glob(hd_wildcard)
      print(hd_wildcard)
      print(files)

   def findBestCrop(self):
      org_x = 1280
      org_y = 720
      max_x = np.amax(self.xs) + 100
      max_y = np.amax(self.ys) + 100
      min_x = np.amin(self.xs) - 100
      min_y = np.amin(self.ys) - 100
      height = max_y - min_y
      width = max_x - min_x
      cx = int((max_x + min_x ) / 2)
      cy = int((max_y + min_y ) / 2)

      if height < 360 and width < 640:
         # we are good to crop a SD image 
         print ('case 1', width, height) 
         # now check to see if the ROI center crop extends beyond the frame, 
         # if so adjust the crop center so it fits.
         if cx + 320 >= 1280:
            cx = 1280 - 320
         if cy + 180 >= 720:
            cy = 720 - 180
         min_x =  cx - 320
         max_x =  cx + 320
         min_y =  cy - 180
         max_y =  cy + 180 
         print ("CX,CY", cx, cy)
         print ("MIN/MAZ X/Y", min_x, max_x,min_y,max_y)
      else: 
         # Just abort and don't make a crop file for now!
         exit()
         # the ROI is larger than SD size, so we will need to be crop it 
         # and rescale before saving
         print ('case 2') 
         if cx + (width / 2) > 1280:
            cx = int(1280 - (width / 2))
         if cy + (height / 2) > 720 :
            cy = int(720 - (width / 2))
         fr = width / 640
         new_height = int(360 * fr)
         print ("FR, W,H:", fr,width, new_height)
         min_x =  int(cx - (width/2))
         max_x =  int(cx + (width/2))
         min_y =  int(cy - (height/2)) 
         max_y =  int(cy + (height/2))

      return(min_x, max_x, min_y, max_y)

   def cropVideo(self):
      # find center x,y and crop around it 640 x 360 (1280/720)
      go = True 
      min_x, max_x, min_y, max_y = self.findBestCrop()

      print ("CROP: ", self.trim_file)
      cap = cv2.VideoCapture(self.trim_file)

      self.crop_file = self.trim_file.replace("trim", "trimcrop")

      cap = cv2.VideoCapture(self.trim_file)
      fourcc = cv2.VideoWriter_fourcc(*'H264')
      height = max_y - min_y
      width = max_x - min_x
      print ("WIDTH, HEIGHT:", width, height)
      out = cv2.VideoWriter(self.crop_file,fourcc, 25, (width,height),1)


      print ("CROP!", self.trim_file)
      frame_count = 0
      while go is True:
         _ , frame = cap.read()
         if frame is None and frame_count > 5:
            go = False
         else:
            print ("FC:", frame_count)
            crop_frame = frame[min_y:max_y, min_x:max_x]
            print(crop_frame.shape)
            out.write(crop_frame)
            cv2.imshow('pepe', crop_frame)
            cv2.waitKey(1)
         frame_count = frame_count + 1
      out.release()

   def trimVideo(self, start, end):
      if self.show_video == 1:
         cv2.namedWindow('pepe')
      if int(start) < 0:
         start = 0
      outfile = self.orig_video_file.replace(".mp4", "-trim-" + str(start) + ".mp4")
      self.trim_file = outfile
      if os.path.isfile(self.orig_video_file) is False:
         print("This file does not exist. Exiting.")
         return(0)
      cap = cv2.VideoCapture(self.orig_video_file)
      fourcc = cv2.VideoWriter_fourcc(*'H264')
      _ , frame = cap.read()
      height, width, x = frame.shape
      out = cv2.VideoWriter(outfile,fourcc, 25, (width,height),1)
      go = True
      self.frame_count = 0
      while go is True:
         _ , frame = cap.read()
         if frame is None:
            go = False
         if int(start) < self.frame_count < int(end):
            print ("Write: ", self.frame_count)
            out.write(frame)
            if self.show_video == 1:
               cv2.imshow('pepe', frame)
         #else: 
            #print ("Skip: ", self.frame_count)
         self.frame_count = self.frame_count + 1
 
      out.release()
      time.sleep(1)

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
         #self.drop_frame()
         #self.move_all_files("day")
         mod_skip = 50
         #return(0)
      else:
         mod_skip = 1 

      if self.show_video == 1:
         cv2.namedWindow('pepe')
      print ("Mod skip is", mod_skip)
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
         print("MAIN VIDEO LOOP")
         if self.frame_count % mod_skip == 0:
            nice_frame_im = Image.fromarray(frame)
            print("MODE", nice_frame_im.mode)
            if self.sun_status == 'day':
               if self.stacked_image is None:
                  nice_frame_im.convert("RGB")
                  #rgb = Image.new("RGBA", nice_frame_im.size)
                  #rgb.paste(nice_frame_im)
                  self.stacked_image = nice_frame_im 
            else:
               if self.stacked_image is None:
                  print("working on the stack...")
                  nice_frame_im.convert("RGB")
                  #rgb = Image.new("RGBA", nice_frame_im.size)
                  #rgb.paste(nice_frame_im)
                  self.stacked_image=ImageChops.lighter(self.stacked_image,nice_frame_im)

   def stillMask(self):
      mask_file = "conf/mask-" + str(self.cam_num) + ".txt"
      file_exists = Path(mask_file)
      mask_exists = 0
      if (file_exists.is_file()):
         print("Mask File found.")
         ms = open(mask_file)
         for lines in ms:
            line, jk = lines.split("\n")
            ex = "self." + str(line)
            exec(ex)
         ms.close()
         mask_exists = 1
      #(sm_min_x, sm_max_x, sm_min_y, sm_max_y) = still_mask
      if mask_exists == 1:
         return(self.still_mask)
      else:
         return(0,0,0,0)

   def save_best_thresh(self, tlimit):
      thresh = "conf/limit-" + self.cam_num + ".txt" 
      fp = open(thresh, "w") 
      fp.write(str(tlimit))
      fp.close()

   def load_best_thresh(self):
      thresh = "conf/limit-" + self.cam_num + ".txt" 

      file_exists = Path(thresh)
      if (file_exists.is_file()):
         fp = open(thresh, "r") 
         for line in fp:
            tlimit = line
      else:
         tlimit = 10

      print ("USING LAST LIMIT", tlimit)
      time.sleep(5)
      return(int(tlimit))

   def mask_bright_areas(self, blur_med, current_image):
      print("BM:", blur_med)
      blur_med = cv2.cvtColor(blur_med, cv2.COLOR_BGR2GRAY)
      current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
      masks = []
      # find bright areas in median and mask them out of the current image
      _, median_thresh = cv2.threshold(blur_med, 40, 255, cv2.THRESH_BINARY)

      (_, cnts, xx) = cv2.findContours(median_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      hit = 0
      real_cnts = []
      if len(cnts) < 1000:
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])
            if True:
               w = w + 10
               h = h + 10
               x = x - 10
               y = y - 10
               if x < 0:
                  x = 0
               if y < 0:
                  y = 0
               if x+w > current_image.shape[1]:
                  x = current_image.shape[1]-1
               if y+h > current_image.shape[0]:
                  y = current_image.shape[0]-1
            if w > 0 and h > 0:
               mask = current_image[y:y+h, x:x+w]
               masks.append((x,y,w,h))
               for xx in range(0, mask.shape[1]):
                  for yy in range(0, mask.shape[0]):
                     mask[yy,xx] = randint(0,6)
               blur_mask = cv2.GaussianBlur(mask, (5, 5), 0)
               current_image[y:y+h,x:x+w] =blur_mask
               blur_med[y:y+h,x:x+w] =mask
      return(current_image, blur_med, masks) 
  
   def find_best_thresh(self, image, thresh_limit):
      go = 1
      thresh_limit = 8  
      if len(image.shape) > 2:
         image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

      for i in range (0,50):
         frame = self.frames[i]
         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         frame = cv2.GaussianBlur(frame, (21, 21), 0) 
         if self.image_acc is None:
            self.image_acc = np.empty(np.shape(frame))

         image_diff = cv2.absdiff(self.image_acc.astype(frame.dtype), frame,)
         alpha = .1 
         hello = cv2.accumulateWeighted(frame, self.image_acc, alpha)



      while go == 1:
         _, thresh = cv2.threshold(image_diff, thresh_limit, 255, cv2.THRESH_BINARY)
         (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         if len(cnts) > 5:
            thresh_limit = thresh_limit + 1
         else:
            bad = 0
            for (i,c) in enumerate(cnts):
               x,y,w,h = cv2.boundingRect(cnts[i])
               if w == image.shape[1]:
                  bad = 1
            if bad == 0:
               go = 0
            else:
               thresh_limit = thresh_limit + 1
         print ("CNTs, BEST THRESH:", str(len(cnts)), thresh_limit)
      #exit()
      return(thresh_limit)


   def find_best_thresh_old(self, tlimit):
      noise = 0 
      go = 1
      attempts = 0
      #make the self.image_acc starter
      for i in range (0,50):
         frame = self.frames[i]
         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         frame = cv2.GaussianBlur(frame, (21, 21), 0) 
         if self.image_acc is None:
            self.image_acc = np.empty(np.shape(frame))

         image_diff = cv2.absdiff(self.image_acc.astype(frame.dtype), frame,)
         alpha = .1 
         hello = cv2.accumulateWeighted(frame, self.image_acc, alpha)


      while go == 1:
         noise = 0
         for i in range (0,100):
            frame = self.frames[i]
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.GaussianBlur(frame, (21, 21), 0) 
            if self.image_acc is None:
               self.image_acc = np.empty(np.shape(frame))

            image_diff = cv2.absdiff(self.image_acc.astype(frame.dtype), frame,)
            alpha = .1 
            hello = cv2.accumulateWeighted(frame, self.image_acc, alpha)
            _, threshold = cv2.threshold(image_diff, tlimit, 255, cv2.THRESH_BINARY)
            thresh= cv2.dilate(threshold, None , iterations=4)
            (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print ("CNTS:", i, len(cnts))
            if len(cnts) > 1:
               noise = noise + 1
         if noise < 3:
            print("Limit is good after tries:",attempts,  tlimit)
            go = 0
            self.save_best_thresh(tlimit)
            break
         else:
            print("Too Much Noise Increase limit:", tlimit)
            tlimit = tlimit + 2
         attempts= attempts + 1 
         if attempts > 10:
            print ("We tried and couldn't fix this!")
            break

      print ("noise at this limit is :", tlimit, noise)
      return(noise, tlimit)

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
         #print ("Skipping daytime files for now.")
         #self.drop_frame()
         #self.move_all_files("day")
         mod_skip = 25 
      else:
         mod_skip = 1 
         if "HD" in self.orig_video_file:
            mod_skip = 1

      if self.show_video == 1:
         cv2.namedWindow('pepe')

      cap = cv2.VideoCapture(self.orig_video_file)
      frame_count = 0
      self.image_acc = None
      last_frame = None
      nostars = 0
      real_motion = 0
      tstamp_prev = 0
      self.events = []
      self.still_mask = self.stillMask()
      (sm_min_x, sm_max_x, sm_min_y, sm_max_y) = self.still_mask
      if "HD" in self.orig_video_file:
         sm_min_y = int(sm_min_y) * .75
         sm_max_y = int(sm_max_y) * .75     
         sm_min_y = int(sm_min_y) * 2     
         sm_max_y = int(sm_max_y) * 2     
         sm_min_x = int(sm_min_x) * 2     
         sm_max_x = int(sm_max_x) * 2     

      #preload video then do analytics
      frames = []
      frame_count = 0
      go = 1
      while go == 1:
         _ , frame = cap.read()
         if frame is None: 
            if frame_count <= 1:
               cap.release()
               print("Bad file.")
               return(0)
            else:
               go = 0
         else:
            self.frames.append(frame)
            frame_count = frame_count + 1
      #while True:
         #print(frame_count, self.motion_events, self.prev_motion)
         #cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,frame_count)
         #_ , frame = cap.read()


      frame_count = 0
      sum_thresh_total = 0
      best_limit = 10
      best_limit = self.load_best_thresh()
      print ("TOTAL FRAMES: ", len(self.frames))
      if len(self.frames) > 100:
         median_img = np.median(np.array(self.frames[0:25]), axis=0)
         median = np.uint8(median_img)
         median_img = median
         masked_median, masked_current,masks = self.mask_bright_areas(median_img, self.frames[0])
         cv2.imshow('pepe', masked_median)
         cv2.waitKey(1000)
         cv2.imshow('pepe', masked_current)
         cv2.waitKey(1000)
         best_limit = self.find_best_thresh(masked_current, best_limit)
      else: 
         best_limit = 10 
         noise = 1 
      #if (noise == 0):
      #   best_limit = best_limit - 2

      cnt_group = []
      self.event_cnts = []
      for frame in self.frames:
         frame_count = frame_count + 1
         print(frame_count)
         self.frame_count = frame_count

         #mask bright areas
         if len(masks) > 0:
            for mx,my,mw,mh in masks:
               if len(frame.shape) > 2:
                  frame[my:my+mh,mx:mx+mw] = [4,4,4]
               else:
                  frame[my:my+mh,mx:mx+mw] = 4
 

         # main video loop
         if frame_count % mod_skip == 0:
            # prep up different versions of the frame as needed
            nice_frame = frame
            if self.show_video == 1:
               nice_frame_small = frame
               nice_frame_small = cv2.resize(frame, (0,0), fx=0.75, fy=0.75) 

            nice_frame_im = Image.fromarray(nice_frame)
            #nice_frame_im = Image.fromarray(cleaned)

            # Apply still mask
            frame[sm_min_y:sm_max_y, sm_min_x:sm_max_x] = [0,0,0]


            # mask out the time for motion detection 
            if self.detect_motion == 1:
               if frame is not None:
                  if frame.shape[1] == 640:
                     masked = frame[440:480, 0:310] 
                     frame[440:480, 0:640] = [0,0,0]
                  else:
                     masked = frame[680:720, 0:620] 
                     frame[670:720, 0:620] = [0,0,0]

               #frame = cv2.resize(frame, (0,0), fx=0.75, fy=0.75) 
               frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
               frame = cv2.GaussianBlur(frame, (21, 21), 0) 
        
               # setup image accumulation 
               if last_frame is None:
                  last_frame = nice_frame
               if self.image_acc is None:
                  self.image_acc = np.empty(np.shape(frame))

               image_diff = cv2.absdiff(self.image_acc.astype(frame.dtype), frame,)
               #alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
               alpha = .1 
               hello = cv2.accumulateWeighted(frame, self.image_acc, alpha)
               _, threshold = cv2.threshold(image_diff, best_limit, 255, cv2.THRESH_BINARY)
               thresh= cv2.dilate(threshold, None , iterations=4)
               (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
              # _, br_threshold = cv2.threshold(frame, 12, 255, cv2.THRESH_BINARY)
              # max_pix = np.max(frame) 
              # sum_thresh = np.sum(br_threshold) / 255
              # sum_thresh_total = sum_thresh_total + sum_thresh
              # sum_thresh_avg = sum_thresh_total / (int(frame_count  ))
              # perc = sum_thresh / sum_thresh_avg
               #print("BRIGHTNESS:", frame_count, max_pix, sum_thresh_avg, sum_thresh, perc)
               #if sum_thresh > (sum_thresh_avg * 1.3):
              #    print ("HIT!")


               if len(cnts) > 0:
                  print("CNTS:", len(cnts))
               real_cnts = []
               if len(cnts) > 0:
                  for (i,c) in enumerate(cnts):
                     x,y,w,h = cv2.boundingRect(cnts[i])
                     cv2.rectangle(frame, (x,y), (x+w, y+h), (255,255,255),2)
                     if w > 2 and h > 2 and frame_count > 8 and (x > 1 and y > 1):
                        real_cnts.append([x,y,w,h])
               if len(real_cnts) >= 1 and frame_count > 60:
                  #self.motion_cnts.append([frame_count,len(cnts),x,y,w,h])
                  cnt_group.append([frame_count,len(cnts),x,y,w,h])
                  self.cx = (self.cx + x)/frame_count
                  self.cy = (self.cx + x)/frame_count
                  self.motion = 1
                  self.total_motion = self.total_motion + 1
                  self.xs.append(x)
                  self.ys.append(y)
                  self.points.append((x,y))
                  self.frame_data.append([frame_count, len(real_cnts),x,y,w,h])
                  if self.prev_motion == 1:
                     self.cons_motion = self.cons_motion + 1
                  else:
                     # startng a new event here
                     self.motion_events = self.motion_events + 1
                     print ("Event Started")

                  if self.motion == 1:
                     self.prev_motion = 1
                  else:
                     self.prev_motion = 0
                  #self.motion_frames.append(frame_count)
                  self.events.append(frame_count)
               else:
                  if self.prev_motion == 1:
                     print ("EVENT ENDED.")
                     self.motion_frames.append((self.events))
                     self.event_cnts.append(cnt_group)
                     self.events = []
                     cnt_group = []
                  real_cnts = []
                  self.frame_data.append([frame_count, len(real_cnts),0,0,0,0])
                  self.motion = 0
                  self.prev_motion = 0


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
                  np_stacked_image = np.asarray(nice_frame)
                  with_stars = self.draw_stars(np_stacked_image)
                  if len(np_stacked_image.shape) > 0 :
                     #stacked_image_small = cv2.resize(with_stars, (0,0), fx=0.5, fy=0.5) 
                     #stacked_image_small = cv2.resize(np_stacked_image, (0,0), fx=0.5, fy=0.5) 
                     stacked_image_small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
                     cv2.imshow('pepe', stacked_image_small)
                     cv2.waitKey(1)

      end_time = int(time.time())
      elapsed = end_time - start_time
      print("Processed ", frame_count, "frames. in ", elapsed, "seconds" )
      cap.release()
      self.cleanup_process()
      #self.analyze_stack()

   def roi_video(self, roi_mn_y, roi_mx_y, roi_mn_x, roi_mx_x):
      frame_count = 0
      print(len(self.frames))
      hits = []
      total_sum = 0
      for frame in self.frames:
         if frame is not None:
            frame_count = frame_count + 1
            roi_frame = frame[roi_mn_y:roi_mx_y, roi_mn_x:roi_mx_x]
            roi_frame = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
            _, roi_thresh = cv2.threshold(roi_frame, 20, 255, cv2.THRESH_BINARY)
            print(roi_frame.shape)

            max_px = np.max(roi_thresh)
            avg_px = np.average(roi_thresh)
            sum_px = np.sum(roi_thresh)
            total_sum = total_sum + sum_px
            avg_sum = total_sum / frame_count 
            print(frame_count, avg_px, max_px, avg_sum, sum_px)
            if (sum_px > (avg_sum * 1.2)):
               print ("HIT!")
            #cv2.imshow('pepe', roi_frame)
            cv2.imshow('pepe', roi_thresh)
            cv2.waitKey(10)


   def analyze_stack(self):
      np_stacked_image = cv2.cvtColor(np.asarray(self.stacked_image), cv2.COLOR_BGR2GRAY)
      np_stacked_diff = cv2.absdiff(self.image_acc.astype(np_stacked_image.dtype), np_stacked_image,)
      _, diff_thresh = cv2.threshold(np_stacked_diff, 20, 255, cv2.THRESH_BINARY)
      points = []
      diff_thresh[400:480, 0:640] = [0]
      (_, cnts, xx) = cv2.findContours(diff_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      if len(cnts) > 0:
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])
            if w > 1 and h > 1:
               print("CNTS: ", i, w,h)
               points.append((x,y))
               cv2.rectangle(diff_thresh, (x,y), (x+w+5, y+h+5), (255),2)
         objects = self.find_objects(0, points)
 
         mx = []
         my = []
         print (objects)
         for object in objects:
            for dist,angle,(x1,y1),(x2,y2) in object:
               print (dist,angle,x1,y1,x2,y2)
               mx.append(x1)
               mx.append(x2)
               my.append(y1)
               my.append(y2)

         print ("OBJECTS FOUND: ", len(objects))
         if len(mx) > 0:
            roi_mx_x = np.max(mx) + 15
            roi_mn_x = np.min(mx) - 15
            roi_mx_y = np.max(my) + 15
            roi_mn_y = np.min(my) - 15
            print("ROI: ", roi_mn_y, roi_mx_y, roi_mn_x, roi_mx_x)
            self.roi_video(roi_mn_y, roi_mx_y, roi_mn_x, roi_mx_x)
            cv2.rectangle(diff_thresh, (roi_mn_x,roi_mn_y), (roi_mx_x, roi_mx_y), (255,255,255),2)
         

      #cv2.imshow('pepe', np_stacked_image)
      #cv2.waitKey(2000)
      cv2.imshow('pepe', np_stacked_diff)
      cv2.waitKey(5000)
      cv2.imshow('pepe', diff_thresh)
      cv2.waitKey(10000)
      return(0)


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
      xl = len(self.xs)
      yl = len(self.ys)
      if xl >= 3 :
         sf = 0 
         mf = int(xl/2)
         ef = xl - 1
         #self.straight_line = self.compute_straight_line(self.xs[sf],self.ys[sf],self.xs[mf],self.ys[mf],self.xs[ef],self.ys[ef])

         rg = self.examine_cnts()
         if rg >= 1:
            self.straight_line = self.is_straight(self.points)
         else:
            self.straight_line = 0

         print("STRAIGHT:", self.straight_line) 

         if self.straight_line == 1 and self.sun_status != 'day' and self.cons_motion < 200 and len(self.motion_frames) < 75:
            self.meteor_yn = "Y"
         else:
            self.meteor_yn = "N"
     
 
      #print("STACK", self.stacked_image)          
      np_stacked_image = np.asarray(self.stacked_image)

      np_star_image = np.asarray(self.star_image_gray)
      #cleaned_stack = morphology.remove_small_objects(np_stacked_image, min_size=2, connectivity=12)

      #cleaned_stack = cv2.fastNlMeansDenoisingColored(np_stacked_image,None,8,8,7,21)
      #cleaned_stars = cv2.fastNlMeansDenoising(np_star_image,None,8,8,7,21)

      #cv2.imwrite(self.stacked_image_fn, np_stacked_image)
      if self.sun_status != 'day' and self.detect_stars == 1: 
         print ("Writing:", self.star_image_fn)
         #cv2.imwrite(self.star_image_fn, np_star_image)
      #cv2.imwrite(self.star_image_fn, cleaned_stars)
      print ("Writing:", self.stacked_image_fn)
      
      #print(np_stacked_image)
      #print ("NP", np_stacked_image)
      #print (np_stacked_image.shape)
      #print (np_stacked_image.dtype)
      #if len(np_stacked_image.shape) >  0:
         #cv2.imwrite(self.stacked_image_fn, np_stacked_image)
      report = "orig_video_file=\"" + self.orig_video_file + "\"\n"
      report = report + "frame_count=" + str(self.frame_count) + "\n"
      report = report + "fps=" + str(self.frame_count/60) + "\n"
      report = report + "sun_status=\"" + self.sun_status + "\"\n"
      report = report + "total_stars=" + str(self.total_stars) + "\n"
      report = report + "star_list=" + str(self.starlist) + "\n"
      report = report + "total_motion=" + str(self.total_motion) + "\n"
      if self.total_motion >= 1:
         report = report + "xs=" + str(self.xs) + "\n"
         report = report + "ys=" + str(self.ys) + "\n"
         report = report + "motion_frames=" + str(self.motion_frames) + "\n"
         report = report + "straight_line=" + str(self.straight_line) + "\n"
         report = report + "meteor_yn=\"" + str(self.meteor_yn) + "\"\n"
         report = report + "motion_events=" + str(self.motion_events) + "\n"
         report = report + "event_cnts=" + str(self.event_cnts) + "\n"
         #report = report + "motion_cnts=" + str(self.motion_cnts) + "\n"
         report = report + "cons_motion=" + str(self.cons_motion) + "\n"
         report = report + "frame_data=" + str(self.frame_data) + "\n"
      # Write out report file.
      print ("Writing: ", self.report_fn)
      fp = open(self.report_fn, "w")
      fp.write(report)
      fp.close()
      #print (report)
      print ("Motion Frames:", str(self.motion_frames))
      print ("Motion Events:" + str(self.motion_events))
      print ("Event CNTS:" + str(self.event_cnts))

      cx = (self.min_x + self.max_x) / 2
      cy = (self.min_y + self.max_y) / 2

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

   def parse_date (self, this_file):

      el = this_file.split("/")
      file_name = el[-1]
      file_name = file_name.replace("_", "-")
      file_name = file_name.replace(".", "-")
      print ("MIKE", this_file, file_name)
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, xext = file_name.split("-")
      cam_num = xcam_num.replace("cam", "")
      self.SetCamNum(cam_num)
      #self.chk_dirs()

      date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
      self.capture_date = date_str
      return(cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec)

   def parse_file_date(self):
      print(self.orig_video_file)
      if ".mp4" in self.orig_video_file:
         self.stacked_image_fn = self.orig_video_file.replace(".mp4", "-stack.jpg") 
         self.star_image_fn = self.orig_video_file.replace(".mp4", "-stars.jpg") 
         self.report_fn = self.orig_video_file.replace(".mp4", "-report.txt") 

         self.trim_file = self.orig_video_file.replace(".mp4", "-trim.mp4")

      else:
         self.stacked_image_fn = self.orig_video_file.replace(".avi", "-stack.jpg") 
         self.trim_file = self.orig_video_file.replace(".avi", "-trim.avi")
         self.star_image_fn = self.orig_video_file.replace(".avi", "-stars.jpg") 
         self.report_fn = self.orig_video_file.replace(".avi", "-report.txt") 
      el = self.orig_video_file.split("/") 
      file_name = el[-1]
      file_name = file_name.replace("-cat", "")
      file_name = file_name.replace("_", "-")
      file_name = file_name.replace(".", "-")
      print ("FILE IS:", file_name)
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, xext = file_name.split("-")
      cam_num = xcam_num.replace("cam", "")
      self.SetCamNum(cam_num)
      #self.chk_dirs() 
    
      date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
      self.capture_date = date_str
      print(self.capture_date, cam_num)


#!/usr/bin/python3
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


def cluster(points):
   brc = Birch(branching_factor=50, n_clusters=3, threshold=.5, compute_labels=True)
   print(brc.fit(points))
   Birch(branching_factor=50, compute_labels=True, copy=True, n_clusters=3, threshold=.5, )
   #return(brc.predict(points))
   return(brc.fit(points))

 

def calc_dist(x1,y1,x2,y2):  
   dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
   return dist  


def find_angle(x1,x2,y1,y2):
   if x2 - x1 != 0:
      a1 = (y2 - y1) / (x2 - x1)
   else:
      a1 = 0
   angle = math.atan(a1)

   angle = math.degrees(angle)
   return(angle)

def find_objects(index, points):
   apoints = []
   sorted_points = []
   last_angle = None
   objects = []
   group_pts = []
   count = 0
   x1,y1 = points[index-count]
   for x1,y1 in points:
      for x2,y2 in points:
         dist = calc_dist(x1,y1,x2,y2)
         angle = find_angle(x1,y1,x2,y2)
         if dist > 10 and dist < 100:
            apoints.append((dist,angle,(x1,y1),(x2,y2)))
         count = count + 1
   sorted_points = sorted(apoints, key=lambda x: x[1])

   for dist,angle,(x1,y1),(x2,y2) in sorted_points:
      if last_angle != None:
         if ((last_angle - 5) < angle < (last_angle + 5)) and (dist > 5 and dist < 70):
            group_pts.append((dist,angle,(x1,y1),(x2,y2)))
            #print ("MATCHING POINTS DX/AN", dist, angle, x1,y1,x2,y2)
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

def confirm_cnts(crop):
   crop = cv2.GaussianBlur(crop, (5, 5), 0)
   avg_flux = np.average(crop)
   max_flux = np.amax(crop)
   thresh_limit = avg_flux / 2 
   _, crop_thresh = cv2.threshold(crop, thresh_limit, 255, cv2.THRESH_BINARY)

   #(_, cnts, xx) = cv2.findContours(crop_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


   #if np.sum(crop_thresh) > (255 * 2):
      #print ("CONFIRM:", max_flux, avg_flux, thresh_limit, np.sum(crop_thresh))
      #cv2.imshow('pepe', crop_thresh)
   #else:
   #   print ("FAILED:", max_flux, avg_flux, thresh_limit, np.sum(crop_thresh))
      #cv2.imshow('pepe', crop)
   #cv2.waitKey(100)
   return(np.sum(crop_thresh)) 

def inspect_image(background, current_image, after_image):
   global avg_cnt
   global avg_tot
   global avg_pts
   rois = []
   image_diff = cv2.absdiff(current_image.astype(current_image.dtype), background,)
   orig_image = current_image
   current_image = image_diff

   avg_flux = np.average(current_image)
   max_flux = np.amax(current_image)
   thresh_limit = avg_flux + ((max_flux - avg_flux ) / 10 )
   print ("FLUX: ", max_flux, avg_flux, thresh_limit)
   points = []
   #edges = cv2.Canny(current_image,thresh_limit,255)
   edges = cv2.Canny(current_image,thresh_limit,255)
   edges[435:480, 0:640] = [0]
   blend = cv2.addWeighted(current_image, .5, edges, .5,0)

   _, blend_thresh = cv2.threshold(blend, thresh_limit, 255, cv2.THRESH_BINARY)

   (_, cnts, xx) = cv2.findContours(blend_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   hit = 0


   real_cnts = []
   if len(cnts) < 1000:
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         if w > 3 and h > 3:
            crop = current_image[y:y+h, x:x+w]
            sum_crop = confirm_cnts(crop)
            if int(sum_crop) > (255 * 5):
               real_cnts.append(cnts[i])

 


   if len(real_cnts) < 1000:
      for (i,c) in enumerate(real_cnts):
         x,y,w,h = cv2.boundingRect(real_cnts[i])
         if w < 25 or h < 25:
            #print(w,h)
            #blend[y:y+h+2,x:x+w+2] = [0]
            #cv2.rectangle(current_image, (x,y), (x+w+5, y+h+5), (255,255,255),1)
            cv2.circle(current_image, (x,y), 20, (120), 1)
            points.append((x,y))

         elif w>=630 and h>=430:
            skip = 1
         else:
            cv2.rectangle(current_image, (x,y), (x+w, y+h), (255),1)
            hit = 1
            rois.append((x,y,x+w,y+h))

      avg_tot = avg_tot + int(len(points))
      if avg_cnt > 0:
         avg_pts = avg_tot / (avg_cnt + 1)
      avg_cnt = avg_cnt + 1


      if len(points) > 3:
         #perc, line_image = is_straight(points, blend_thresh)
         objects = find_objects(0, points)
      else:
         line_image = blend_thresh
         objects = []
    
      if len(objects) > 0:
         hit = 1


      if hit == 1:
         text = "hit"
         disp =  current_image

         xs = []
         ys = []
         for obj in objects:
            for dist,angle,(x1,y1),(x2,y2) in obj:
               cv2.line(disp, (x1,y1), (x2,y2), (255), 2)    
               xs.append(x1)
               xs.append(x2)
               ys.append(y1)
               ys.append(y2)

         if len(xs) > 0:
            max_x = np.max(xs)
            min_x = np.min(xs)
            max_y = np.max(ys)
            min_y = np.min(ys)
            rois.append((min_x,min_y,max_x,max_y))

         cv2.putText(disp, text,  (100,100), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)

         print ("CNTS:", len(cnts))
         print ("REAL CNTS:", len(real_cnts))
         print ("POINTS:", len(points))
         print ("AVG POINTS:", avg_pts)
         print("OBJECTS:", len(objects))
         if len(points) * 2 > avg_pts:
            hit = 1
         if len(objects) > 10:
            hit = 0 

         mmx = 0
         mmy = 0
         mnx = 0
         mny = 0
         if hit == 1:
            for min_x, min_y, max_x, max_y in rois:
               skip_roi = 0
               for mnx, mny, mmx, mmy in rois:
                  if min_x < mnx and min_y < mny and max_x < mmx and max_y < mmy:
                     print ("This ROI exists inside another so skip it!")
                     skip_roi = 1
               if skip_roi == 0:
                  cv2.rectangle(disp, (min_x,min_y), (max_x, max_y), (255),2)

         blend = cv2.addWeighted(orig_image, .9, disp, .1,0)
         cv2.imshow('pepe', blend)
         cv2.waitKey(1)
      else: 
         text = "failed"
         disp =  current_image
         print ("CNTS:", len(cnts))
         print ("REAL CNTS:", len(real_cnts))
         print ("POINTS:", len(points))
         print("OBJECTS:", len(objects))
         cv2.putText(disp, text,  (100,100), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
         cv2.imshow('pepe', disp)
         cv2.waitKey(1)
   else:
      print("TOO MANY COUNTOURS!", len(cnts))



   return(hit)

def parse_file_date(orig_video_file):
   print(orig_video_file)
   if ".mp4" in orig_video_file:
      stacked_image_fn = orig_video_file.replace(".mp4", "-stack.jpg") 
      star_image_fn = orig_video_file.replace(".mp4", "-stars.jpg")
      report_fn = orig_video_file.replace(".mp4", "-report.txt")

      trim_file = orig_video_file.replace(".mp4", "-trim.mp4")

   else:
      stacked_image_fn = orig_video_file.replace(".avi", "-stack.jpg") 
      trim_file = orig_video_file.replace(".avi", "-trim.avi")
      star_image_fn = orig_video_file.replace(".avi", "-stars.jpg")
      report_fn = orig_video_file.replace(".avi", "-report.txt")
      el = orig_video_file.split("/")
      file_name = el[-1]
      file_name = file_name.replace("_", "-")
      file_name = file_name.replace(".", "-")
      print ("FN", file_name)
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype, xext = file_name.split("-")
      cam_num = xcam_num.replace("cam", "")

      date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
      capture_date = date_str
      return(capture_date)


def day_or_night(config, capture_date):

   obs = ephem.Observer()

   obs.pressure = 0
   obs.horizon = '-0:34'
   obs.lat = config['device_lat']
   obs.lon = config['device_lng']
   obs.date = capture_date

   sun = ephem.Sun()
   sun.compute(obs)

   (sun_alt, x,y) = str(sun.alt).split(":")

   saz = str(sun.az)
   (sun_az, x,y) = saz.split(":")
   print ("SUN", sun_alt)
   if int(sun_alt) < -1:
      sun_status = "night"
   else:
      sun_status = "day"
   return(sun_status)


diffed_files = []
sdate = sys.argv[1]
cam_num = sys.argv[2]
config = read_config("conf/config-1.txt")
video_dir = "/mnt/ams2/SD/"
images = []


glob_dir = video_dir + cam_num + "/time_lapse/" + sdate + "*.jpg"
report_file = video_dir + cam_num + "/time_lapse/" + sdate + ".txt"


cv2.namedWindow('pepe')
mask_file = "conf/mask-" + str(cam_num) + ".txt"
file_exists = Path(mask_file)
mask_exists = 0
if (file_exists.is_file()):
   print("File found.")
   ms = open(mask_file)
   for lines in ms:
      line, jk = lines.split("\n")
      exec(line)
   ms.close()
   mask_exists = 1
   (sm_min_x, sm_max_x, sm_min_y, sm_max_y) = still_mask




diffs = 0
image_list = []
file_list = []
sorted_list = []
print (glob_dir)
fp = open(report_file, "w")
for filename in (glob.glob(glob_dir)):
    capture_date = parse_file_date(filename)
    sun_status = day_or_night(config, capture_date)
    if sun_status != 'day':
       print("NIGHTTIME", capture_date, filename, sun_status)
       file_list.append(filename)
    else:
       print ("DAYTIME!", capture_date, filename, sun_status)

sorted_list = sorted(file_list)
for filename in sorted_list:
   open_cv_image = cv2.imread(filename,0)
   open_cv_image[440:480, 0:640] = [0]
   if mask_exists == 1:
      open_cv_image[sm_min_y:sm_max_y, sm_min_x:sm_max_x] = [0]
   images.append(open_cv_image)

#exit()
#time.sleep(5)
height , width =  open_cv_image.shape

# Define the codec and create VideoWriter object
#fourcc = cv2.VideoWriter_fourcc(*'H264')
#out = cv2.VideoWriter(outfile,fourcc, 5, (width,height),1)

count = 0
last_image = None
last_thresh_sum = 0
hits = 0

avg_cnt = 0
avg_tot = 0
avg_pts = 0
count = 0
for filename in sorted_list:
   hit = 0
   detect = 0
   el = filename.split("/")
   fn = el[-1]
   #this_image = cv2.imread(filename,1)
   this_image = images[count]


   if count >= 1:
      before_image = images[count-1]
   else:
      before_image = images[count+2]

   if count >= len(file_list)-1:
      after_image = images[count-2]
   else:
      after_image = images[count+1]

   if count < 8:
      med_stack = (images[count+1],images[count+2], images[count+3], images[count+4], images[count+5], images[count+6], images[count+7], images[count+8])
   else:
      med_stack = (images[count-1],images[count-2], images[count-3], images[count-4], images[count-5], images[count-6], images[count-7], images[count-8])
   median = np.median(np.array(med_stack), axis=0)
   median = np.uint8(median)
   median_sum = np.sum(median)
  
   if count < 10:
      background = images[count+1] 
      for i in range (0,10):
         background = cv2.addWeighted(background, .8, images[count+i], .2,0)
   else:
      background = images[count-1] 
      for i in range (0,10):
         background = cv2.addWeighted(background, .8, images[count-i], .2,0)

   result = inspect_image(background, this_image, after_image) 

   image_diff = cv2.absdiff(this_image.astype(this_image.dtype), background,)
   _, diff_thresh = cv2.threshold(image_diff, 20, 255, cv2.THRESH_BINARY)
   sum_diff = np.sum(diff_thresh)
   print("SUM DIFF:", sum_diff)
   hits = hits + result
   hit = result
   masked = this_image[440:480, 0:640]

   count = count + 1
   fp.write(fn + "," + str(hit) + "," + str(sum_diff) + "\n")
print ("TOTAL: ", len(file_list))
print ("DIFFS: ", diffs)
print ("HITS: ", hits)
fp.close()


for file in diffed_files:
   el = file.split("/")
   st = el[-1]
   report_str = st.replace("-stack.jpg", "-report.txt")
   video_str = st.replace("-stack.jpg", ".mp4")
   #cmd = "grep \"Motion Frames:\" `find /mnt/ams2/SD/"  + str(cam_num) + " |grep " + report_str + "`" 
   #output = subprocess.check_output(cmd, shell=True).decode("utf-8")

   #output = output.replace("Motion Frames:", "motion_frames=")
   #print (output)
   #exec(output)
   #if len(motion_frames) > 14:
   #   cmd = "find /mnt/ams2/SD/"  + str(cam_num) + " |grep " + video_str 
   #   video_file = subprocess.check_output(cmd, shell=True).decode("utf-8")
   #   print("This is probably a real event?")
   #   print(video_file)
    


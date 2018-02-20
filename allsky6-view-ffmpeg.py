#!/usr/bin/python3
#import skvideo.io
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


video_dir = "/media/ams/Samsung_T5/video/"
video_motion_dir = "/media/ams/Samsung_T5/video/motion/"
video_no_motion_dir = "/media/ams/Samsung_T5/video/no_motion/"


def find_flux(x,y,size,image):
   box = (x-size,y-size,x+size,y+size)
   new_image = Image.fromarray(image)

   flux_box = new_image.crop(box)
   flux_box = flux_box.resize((75,75), Image.ANTIALIAS)
   gray_flux_box = flux_box.convert('L')

   np_flux_box = np.asarray(gray_flux_box)
   np_flux_box = cv2.GaussianBlur(np_flux_box, (21, 21), 0)
   avg_flux = np.average(np_flux_box)
   max_flux = np.amax(np_flux_box)

   ffw= int(np_flux_box.shape[1] / 2)
   ffh = int(np_flux_box.shape[0] / 2)

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
      cv2.putText(np_flux_box, tag, (2, np_flux_box.shape[0] - 2), cv2.FONT_HERSHEY_SIMPLEX, .3, (255, 255, 255), 1)
      cv2.circle(np_flux_box, (cxx,cxy), 10, (255,255,255), 1)

      return (int(avg_flux), int(max_flux), int(total_flux))
   else:
      return (int(0), int(0), int(0))


def mkdirs(cam_num):
   os.system("mkdir ffvids/" + cam_num + "/calvid")
   os.system("mkdir ffvids/" + cam_num + "/clouds")
   os.system("mkdir ffvids/" + cam_num + "/day")
   os.system("mkdir ffvids/" + cam_num + "/dist")
   os.system("mkdir ffvids/" + cam_num + "/false")
   os.system("mkdir ffvids/" + cam_num + "/maybe")
   os.system("mkdir ffvids/" + cam_num + "/no_motion_day")
   os.system("mkdir ffvids/" + cam_num + "/no_motion_night")
   os.system("mkdir ffvids/" + cam_num + "/stars")


def day_or_night(config, video_date):

   obs = ephem.Observer()

   print ("DATE:", video_date)

   obs.pressure = 0
   obs.horizon = '-0:34'
   obs.lat = config['device_lat']
   obs.lon = config['device_lng']
   obs.date = video_date 

   sun = ephem.Sun()
   sun.compute(obs)

   (sun_alt, x,y) = str(sun.alt).split(":")
   print ("Date: %s" % (video_date))
   print ("Sun Alt: %s" % (sun_alt))

   saz = str(sun.az)
   (sun_az, x,y) = saz.split(":")
   print ("SUN AZ IS : %s" % sun_az)

   if int(sun_alt) < -5: 
      status = "night"
   else: 
      status = "day"
   return(status)

def main():
#   cam_num = "1"
   try:
      file = sys.argv[1]
      batch = 0
   except:
      #files = glob.glob(video_dir + cam_num + "/*.mp4")
      batch = 1
   if file == "batch":
      
      cam_num = sys.argv[2]
      mkdirs(cam_num)
      print("Batch mode for cam_num:", cam_num)
      files = glob.glob(video_dir + cam_num + "/*.mp4")
      batch = 1

   try:
      show = sys.argv[2]
   except:
      show = 0

   if batch == 0:
      view(file, show)
   else: 
      for file in sorted(files):
         view(file) 

def read_time_file(file):
   extra_data = "";
   frame_data = []
   print ("Reading time file: ", file)

   file = open(file, "r")
   for line in file:
      try:
         line = line.strip('\n')
         data = line.split("|")
         extra_data = data[2] + "|" + data[3] + "|" + data[4] + "|" + data[5] 
      except:
         print ("Empty lines in time data");
      frame_data.append(extra_data);

   return(frame_data)


def view(file, show = 0):
   nostars = 0
   skip = 0 
   avg_color = 0 
   max_cons_motion = 0 
   straight_line = -1
   final_image = None
   start_time = int(time.time())

   el = file.split("/")
   act_file = el[-1]
   dir = file.replace(act_file, "")

   acc_file = act_file.replace(".mp4", "-acc.jpg")
   star_file = act_file.replace(".mp4", "-stars.jpg")

   acc_file = dir + "stars/" + acc_file
   star_file = dir + "stars/" + star_file

   # before processing dump frames from this file for 24 hour time lapse
   #os.system("./dump-frames-tl.py " + file )

   config_file = ""
   try:
      (file_date, cam_num) = file.split("-")
      cam_num = cam_num.replace(".avi", "")
   except:
      cam_num = ""

   if cam_num == "":
      config = read_config(config_file)
   else: 
      #cam_num = sys.argv[1]
      config_file = "conf/config-" + cam_num + ".txt"
      config = read_config(config_file)



   #config = read_config(config_file)
   frame_time_data = []
   values = {}
   dir_name = os.path.dirname(file) + "/" 
   file_name = file.replace(dir_name , "")
   summary_file_name = file_name.replace(".mp4", "-summary.txt")
   data_file_name = file_name.replace(".mp4", ".txt")
   screen_cap_file_name = file_name.replace(".mp4", ".jpg")
   object_file_name = file_name.replace(".mp4", "-objects.jpg")
   time_file_name = file_name.replace(".mp4", "-time.txt")
   capture_date = parse_file_date(file_name)
   #last_cal_date = # Get last / closest calibration date
   file_base_name = file_name.replace(".mp4", "") 
   print (capture_date)
   status = day_or_night(config, capture_date)

   if status == "day":
      print ("Skip this daytime file.")
      move_file(dir_name + file_name, "day")
      return()

   # read in time file if it exists
   
   #if os.path.isfile(dir_name + "/" + time_file_name):
   #   frame_time_data = read_time_file(dir_name + "/" + time_file_name)
   #   print ("FRAME TIME DATA LENGTH:", len(frame_time_data))
   #   time.sleep(1)
   #else: 
   #   print ("no frame time data! " + dir_name + "/" + time_file_name ) 
   #   for x in range(0, 225): 
   #      frame_time_data.append("|||")


   #fps_t = 0
   #for ftd in frame_time_data:
   #   print ("FRAMEdata", ftd)
   #   fps, tc, tt, tx = ftd.split("|")
   #   if fps == "":
   #      fps = 0
   #   fps_t = int(float(fps_t)) + int(float(fps))
   #if len(frame_time_data) > 0:
   #   avg_fps = fps_t / len(frame_time_data)
   #else :
   #   avg_fps = 0

   avg_fps = 25 

   print ("Viewing file: " + file)
   print ("Directory: " + dir_name)
   print ("File Name: " + file_name)
   print ("Summary File Name: " + summary_file_name)
   print ("Data File Name: " + data_file_name)
   print ("Screen Cap File Name: " + screen_cap_file_name)
   print ("Object File Name: " + object_file_name)
   print ("Capture Date: " + capture_date)
   #print ("FPS: " + str(avg_fps))

   # make sure the file exists
   if os.path.isfile(file) is False:
      print("This file does not exist. Exiting.")
      return(0)
   else:
      print ("The file is ok.")

   #process video

   tstamp_prev = None
   image_acc = None
   last_frame = None
   last_gray_frame = None
   nt_acc = None
   nice_image_acc = None
   final_image = None
   cur_image = None
   frame_count = 0

   # open data log file
   #fp = open(dir_name + "/" + data_file_name, "w")
   #fp2 = open(dir_name + "/" + summary_file_name, "w")
   #fp.write("frame|contours|x|y|w|h|color|fps|adjusted_unixtime|unixtime|time_offset\n")
   #fp2.write("frame|contours|x|y|w|h|color|fps|adjusted_unixtime|unixtime|time_offset\n")

   show = 1
   if show == 1:
      cv2.namedWindow('pepe') 


   #cap = skvideo.io.VideoCapture(file)
   cap = cv2.VideoCapture(file)
   time.sleep(2)
   xs = []
   ys = []
   motion_frames = []
   frames = []
   colors = []

   show_sw = 0

   noise = 0
   prev_motion = 0
   cons_motion = 0
   motion_events = []

   while True:
      _ , frame = cap.read()
      if frame is not None:
         frame[680:720, 0:620] = [0,0,0]
      frame_count = frame_count + 1
      #frames.extend([frame])


      if frame is None or nostars > 5:
         if frame_count <= 1:
            print("Bad file.")
            return(0)
         else:
            end_time = int(time.time())
            elapsed = end_time - start_time
            print("Processed ", frame_count, "frames. in ", elapsed, "seconds" )
            # finish processing file and write output files

            total_motion = len(motion_frames)

            if total_motion >3:   
               half_motion = int(round(total_motion/2,0))
               print ("key frame #1 : ", 1) 
               print ("key frame #2 : ", half_motion) 
               print ("key frame #3 : ", total_motion -1) 
               print ("Xs", xs)
               print ("Ys", ys)
               print ("MF", motion_frames)
               avg_color = sum(colors) / float(len(colors))
     
               print ("CL", colors)
               print ("Avg Color: ", avg_color)


               #object_file_image = (frames[motion_frames[1]] * .33) + (frames[motion_frames[half_motion]] * .33) + (frames[motion_frames[total_motion-2]] * .33) 
     
               x1 = xs[1]
               y1 = xs[1]
               x2 = xs[half_motion]
               y2 = xs[half_motion]
               x3 = xs[total_motion-2]
               y3 = xs[total_motion-2]

               xmax = max(xs)
               ymax = max(ys)
               xmin = min(xs)
               ymin = min(ys)
               skip = 0

               if xmax - xmin == 0 and ymax - ymin == 0:
                  skip = 1

               straight_line = compute_straight_line(x1,y1,x2,y2,x3,y3)
               if len(motion_events) > 3:
                  max_cons_motion = max(motion_events)
               if (straight_line < 1 and straight_line >= 0) or avg_color > 190:
                  meteor_yn = "Y"
               else:
                  meteor_yn = "N"

            if status == 'night':
               meteor_yn = "Y"
            else:
               meteor_yn = "N"

            if total_motion <= 3:
               meteor_yn = "N"

            #meteor_yn = "Y"
            if skip == 1:
               meteor_yn = "N"
               print ("Skipping not enough x,y movement!", xmax, xmin, ymax, ymin)
            if noise >= 5:
               meteor_yn = "N"
               print ("Skipping to much noise!", noise)
            if avg_fps < 20:
               meteor_yn = "N"
               print ("Skipping calibration file!", avg_fps)

            # write out the stacked image_acc and the stacked star file
            # nt_acc

            print("Writing:", acc_file)
            print("Writing:", star_file)

            #image_acc_cl = cv2.cvtColor(image_acc, cv2.COLOR_GRAY2BGR)
            #en_image_acc = Image.fromarray(cv2.convertScaleAbs(image_acc))

            enhancer = ImageEnhance.Brightness(final_image)
            enhanced_image = enhancer.enhance(1)
            np_enhanced_image = np.asarray(enhanced_image)
            #cv2.imwrite(acc_file, np_enhanced_image)

            #np_final_image = np.asarray(final_image)
            total_stars, star_image = find_stars(np_final_image)
            if total_stars == 0:
               star_file = star_file.replace("/stars/", "/clouds/")
               acc_file = acc_file.replace("/stars/", "/clouds/")
            cv2.imwrite(acc_file, np_enhanced_image)

            #total_stars, star_image = find_stars(cv2.convertScaleAbs(image_acc))

            if total_stars > 0:
               cv2.imwrite(star_file, star_image)
            #cv2.imshow('pepe', star_image)
            #cv2.waitKey(100) 

            print ("Status:", status)
            print ("Total Motion:", total_motion)
            print ("Cons Motion:", cons_motion)
            print ("Straight Line:", straight_line)
            print ("Likely Meteor:", meteor_yn)


            #obj_outfile = dir_name + "/" + object_file_name
            #sc_outfile = dir_name + "/" + screen_cap_file_name 
            #cv2.imwrite(obj_outfile, object_file_image)
            #cv2.imwrite(sc_outfile, object_file_image)


            #write summary & data files

            #fp.close()
            #fp2.close()
            # prep event or capture for upload to AMS
            values['datetime'] = capture_date 
            values['motion_frames'] = total_motion 
            values['cons_motion'] = max_cons_motion
            values['color'] = avg_color
            values['straight_line'] = straight_line
            values['meteor_yn'] = meteor_yn
            values['bp_frames'] = total_motion

            if meteor_yn == 'Y':
               try:
                  values['best_caldate'] = config['best_caldate']
               except:
                  config['best_caldate'] = '0000-00-00 00:00:00';
                  values['best_caldate'] = config['best_caldate']
               #try:
                  #log_fireball_event(config, file, dir_name + "/" + summary_file_name, dir_name + "/" + object_file_name, values)
               #except:
               #   print ("failed to upload event file.")
               #   return(0)
               #move files to maybe dir
               print ("Move to maybe dir!")
               #os.system("mv " + dir_name + "/" + file_base_name + "* " + "/var/www/html/out/maybe/") 
             
               move_file(dir_name + file_name, "maybe")



            else:
               #log_motion_capture(config, dir_name + "/" + object_file_name, values)
               #try:
                   #log_motion_capture(config, dir_name + "/" + object_file_name, values)
               #except:
               #   print ("failed to upload capture file.")
               #   return(0)
               #print ("Move to false dir!")
               if (skip == 1 or noise >= 5) and status == 'night': 
                  #os.system("mv " + dir_name + "/" + file_base_name + "* " + "/var/www/html/out/dist/") 
                  move_file(dir_name + file_name, "dist")


               elif avg_fps < 20:
                  move_file(dir_name + file_name, "calvid")
               else:
                  if total_motion >= 3:
                     move_file(dir_name + file_name, "false")
                  else:
                     move_file(dir_name + file_name, "no_motion_night")

            return(1)

      # main video processing loop here
      if status == "day":
         mod_skip = 5 
      else:
         mod_skip = 5

      if frame_count % mod_skip == 0:
         nice_frame = frame

         alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
         frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
         #print ("AFTER:", np.shape(frame))

         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         gray_frame = frame 
        # if last_gray_frame is None:
        #    last_gray_frame = gray_frame 
        # else:
        #    gray_frame_cmb = gray_frame + last_gray_frame
        #    last_gray_frame = gray_frame 
        #    gray_frame = gray_frame_cmb
         

         frame = cv2.GaussianBlur(frame, (21, 21), 0)
         if last_frame is None:
            last_frame = nice_frame
         if image_acc is None:
            image_acc = np.empty(np.shape(frame))


         image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
         alpha = .076
         hello = cv2.accumulateWeighted(frame, image_acc, alpha)
         _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
         thresh= cv2.dilate(threshold, None , iterations=2)
         (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

         frame_img = Image.fromarray(frame)
         if final_image is None:
            final_image = frame_img
         final_image=ImageChops.lighter(final_image,frame_img)

         if frame_count > 5:
            np_final_image = np.asarray(final_image)
            total_stars, star_image = find_stars(np_final_image)
            if total_stars == 0:
               print("Cloudy...???")
               nostars = nostars + 1
            else:
               nostars = 0
         # if you want to stack the accumulated frames..
         #image_acc_pil = Image.fromarray(cv2.convertScaleAbs(image_acc))
         #final_image=ImageChops.lighter(final_image,image_acc_pil)


         data = str(frame_count) + "|"

         color = 0
         contours = len(cnts)
         x,y,w,h = 0,0,0,0

         if contours > 3:
            noise = noise + 1

         if contours > 0 and frame_count > 5:
            x,y,w,h = cv2.boundingRect(cnts[0])
            mx = x + w
            my = y + h
            cx = int(x + (w/2))
            cy = int(y + (h/2))
            color = gray_frame[cy,cx]
            xs.extend([x])
            ys.extend([y])
            colors.extend([color])

            motion_frames.extend([frame_count])
            prev_motion = 1
            cons_motion = cons_motion +1 
         else:
            if cons_motion > 0:
               motion_events.append(cons_motion)
            prev_motion = 0
          
         line_data = ""   
         #line_data = str(frame_count) + "|" + str(contours) + "|" + str(x) + "|" + str(y) + "|" + str(w) + "|" + str(h) + "|" + str(color) + "|" + frame_time_data[frame_count-1] + "\n"

         #fp.write(line_data)
         #fp2.write(line_data)
         print (frame_count, contours, x,y,w,h,color)
         if frame_count % 10 == 0:
            np_final_image = np.asarray(final_image)
            #cv2.imshow('pepe', np_final_image)
            #cv2.imshow('pepe', cv2.convertScaleAbs(image_acc))
            #cv2.waitKey(1) 

         #if frame_count % 2 == 0:
         #  cv2.imshow('pepe', frame)
         #   cv2.waitKey(1) 
         # END MAIN VIDEO LOOP HERE

   # we will never make it to here cause the program ends when the loop ends. look up.  

def find_stars(star_image):
   # find stars
   total_stars = 0
   star_image_gray = star_image

   cloudy = 0
#cv2.cvtColor(star_image, cv2.COLOR_BGR2GRAY)

   avg_px = np.average(star_image_gray)
   ax_pixel = np.amax(star_image_gray)
   print ("AVG PX, BRIGHT PX", avg_px, ax_pixel)
   #lower_thresh = ax_pixel - 10
   bp_dif = ax_pixel - avg_px
   lower_thresh = avg_px + (bp_dif / 2)
   if avg_px * 2 > ax_pixel or ax_pixel < 60:
      print ("there are no stars, likely cloudy... should skip.")
      total_stars = 0 
      cloudy = 1
   else:
      #lower_thresh = avg_px * 3
      star_image_gray = cv2.GaussianBlur(star_image_gray, (1, 1), 0)
      _, nice_threshold = cv2.threshold(star_image_gray, lower_thresh, 255, cv2.THRESH_BINARY)
      (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      contours = len(cnts)
      size=6
      print ("Cloudy:", cloudy)
      if contours > 0 and cloudy == 0:
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])
            avg_flux, max_flux, total_flux = find_flux(x,y,size,star_image_gray)

            if avg_flux > 0:
               ff = max_flux / avg_flux
            else:
               avg_flux = 1
            if max_flux > 30 and (w < 6 and h < 6) and ff > 2.5:
               print ("Passed flux test")
               cv2.circle(star_image_gray, (x,y), 3, (255), 1)
               total_stars = total_stars + 1
            else:
               print ("Failed flux test")
   return(total_stars, star_image_gray)


def move_file(file, dest_dir):
   print (file, dest_dir)
   el = file.split("/")
   ff = el[-1]
   new_filename = file.replace(ff, "")
   new_filename = new_filename + dest_dir + "/" + ff
   cmd =  "mv " + file + " " + new_filename
   print(cmd)
   os.system(cmd)


def compute_straight_line(x1,y1,x2,y2,x3,y3):
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

def read_time_offset_file(file):
   print("Checking if time offset file exists.")


def parse_file_date(file_name):

#capture-2018-02-17_17-20-30.mp4
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
   return(date_str)

def log_fireball_event(config, maybe_file, maybe_summary_file, maybe_object_file, values) :

   print ("logging fireball event") 
   temp_maybe_file = maybe_file.replace("/var/www/html/out/", "")
   a,b = temp_maybe_file.split("-");
   temp_maybe_file = "/var/www/html/out/temp_upload/" + a + ".avi"

   temp_maybe_summary_file = maybe_summary_file.replace("/var/www/html/out/", "")
   a,b,c = temp_maybe_summary_file.split("-");
   temp_maybe_summary_file = "/var/www/html/out/temp_upload/" + a + ".txt"

   temp_maybe_object_file = maybe_object_file.replace("/var/www/html/out/", "")
   a,b,c = temp_maybe_object_file.split("-");
   temp_maybe_object_file = "/var/www/html/out/temp_upload/" + a + ".jpg"

   cmd = "cp " + maybe_file + " " + temp_maybe_file
   os.system(cmd)
   cmd = "cp " + maybe_object_file + " " + temp_maybe_object_file
   os.system(cmd)
   cmd = "cp " + maybe_summary_file + " " + temp_maybe_summary_file
   os.system(cmd)

   url = settings.API_SERVER + "members/api/cam_api/log_fireball_event"
   _data = {
    'api_key': config['api_key'],
    'device_id': config['device_id'],
    'datetime': values['datetime'],
    'motion_frames' : values['motion_frames'],
    'cons_motion': values['cons_motion'],
    'color' : int(values['color']),
    'straight_line' : values['straight_line'],
    'bp_frames' : values['bp_frames'],
    'format': 'json',
    'meteor_yn': values['meteor_yn']
   }


   summary = maybe_summary_file.replace("-summary", "")
   #if os.path.isfile(maybe_summary_file):
   #   os.system("mv " + maybe_summary_file + " " + summary)
   #   print("mv " + maybe_summary_file + " " + summary)

   event_stack = maybe_object_file.replace("-objects", "")
   event = maybe_file
   #time.sleep(1)
   #os.system("cat " + summary + "> /tmp/sum.txt")
   print (temp_maybe_object_file, event_stack)
   print (temp_maybe_file, event)
   print (temp_maybe_summary_file, summary)

   #"event_stack": " jpg image (FILE)",
   #"event": " avi video (FILE)",
   #"summary": " txt summary of event per frame (FILE)"

   _files = {'event_stack': open(temp_maybe_object_file, 'rb'), 'event':open(temp_maybe_file, 'rb'), 'summary':open(temp_maybe_summary_file, 'r') }

   print ("Summary TXT: ", summary)
   session = requests.Session()
   del session.headers['User-Agent']
   del session.headers['Accept-Encoding']

   with requests.Session() as session:
      response = session.post(url, data= _data, files=_files)

   print (response.text)
   response.raw.close()
   time.sleep(1)
   cmd = "rm " + temp_maybe_file
   os.system(cmd)
   cmd = "rm " + temp_maybe_object_file
   os.system(cmd)
   cmd = "rm " + temp_maybe_summary_file
   os.system(cmd)

def log_motion_capture(config, file, values):
   print ("log motion capture");
   stack_file = file.replace("-objects", "")
   os.system("cp " + file + " " + stack_file)

   temp_maybe_object_file = stack_file.replace("/var/www/html/out/", "")
   a,b = temp_maybe_object_file.split("-");
   temp_maybe_object_file = "/var/www/html/out/temp_upload/" + a + ".jpg"
   cmd = "cp " + stack_file + " " + temp_maybe_object_file
   os.system(cmd)

   url = settings.API_SERVER + "/members/api/cam_api/log_motion_capture"
   _files = {'event_stack': open(temp_maybe_object_file, 'rb')}


   _data = {
    'api_key': config['api_key'],
    'device_id': config['device_id'],
    'cons_motion': values['cons_motion'],
    'color' : int(values['color']),
    'straight_line' : values['straight_line'],
    'bp_frames' : values['bp_frames'],
    'format': 'json',
    'meteor_yn': values['meteor_yn']
   }
   session = requests.Session()
   del session.headers['User-Agent']
   del session.headers['Accept-Encoding']

   with requests.Session() as session:
      response = session.post(url, data= _data, files=_files)

   print (response.text)
   response.raw.close()
   cmd = "rm " + temp_maybe_object_file
   os.system(cmd)



if __name__ == '__main__':
   main()

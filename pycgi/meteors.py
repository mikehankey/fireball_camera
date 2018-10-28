#!/usr/bin/python3
import cv2
import numpy as np
from PIL import Image
from PIL import ImageChops
from collections import defaultdict
#from random import *
import random
import glob
import subprocess
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"
from pathlib import Path
import math, operator 
import functools
print ("Content-type: text/html\n\n")

def get_meteor_stacks(day ):
   meteors = []

   files = glob.glob("/mnt/ams2/meteors/" + str(day) + "/*stacked.jpg")
   for file in files:
      meteors.append(file)
   return(sorted(meteors, reverse=True))

def show_meteor_frames(frame_dir):
   files = sorted(glob.glob(frame_dir + "/*frame*.jpg"))
   fc = 0

   image_acc = None
   motion_frames = [] 
   frame_cnts = [] 
   for file in files:
      im1 = cv2.imread(file)
      gray_frame = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
      gray_frame[440:480, 0:640] = [0]
      gray_file = file.replace(".jpg", "-gray.jpg")
      if image_acc is None:
         image_acc = np.empty(np.shape(gray_frame))
      hello = cv2.accumulateWeighted(gray_frame.copy(), image_acc, .5)
      image_diff = cv2.absdiff(image_acc.astype(gray_frame.dtype), gray_frame,)
      thresh = cv2.adaptiveThreshold(image_diff,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,-20)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      if len(cnts) > 0:
         print(" FC is ", fc)
         motion_frames.append(fc)
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[0])
            cv2.circle(gray_frame, (int(x), int(y)), w+5, 255)
      frame_cnts.append(cnts)
      cv2.imwrite(gray_file, gray_frame)
      fc = fc + 1

   if len(motion_frames) > 0:
      print("MOTION FRAMES", motion_frames)
      first_frame = np.min(motion_frames)
      last_frame = np.max(motion_frames)
      print ("FIRST/LAST FRAME FROM CLIP: ", first_frame, last_frame)
      c = 0
 
      for file in files:
         cnts = frame_cnts[c]
         gray_file = file.replace(".jpg", "-gray.jpg")
         if first_frame -10 < c < last_frame + 5:
            print ("<BR><img src=" + file + "><img src=" + gray_file + "><BR>" + str(len(cnts)) + "<BR>") 
         else:
            print ("<BR><img src=" + file + " width=320 height=240><BR>" + str(len(cnts)) + "<BR>") 
         c = c + 1

def dump_frames(meteor_trim):
   #print ("DUMP FRAMES")
   el = meteor_trim.split("/")
   meteor_file = el[-1]
   meteor_frame_dir = meteor_file.replace(".mp4", "-frames")
   meteor_dir = meteor_trim.replace(meteor_file, "")
   new_meteor_dir = meteor_dir + meteor_frame_dir
   if os.path.exists(new_meteor_dir):
      trash = 1 
      cmd = "rm " + new_meteor_dir + "/*.jpg" 
      print (cmd)
      os.system(cmd)
      #print ("already done.")
   else:
      os.mkdir(new_meteor_dir)

   cmd = "ffmpeg -i " + meteor_trim + " " + new_meteor_dir + "/frame%04d.jpg -qscale:v 2 -hide_banner"
   os.system(cmd)
   #print (cmd)
   #print ("<BR>")
   cmd = "mv " + meteor_dir + "*frame* " + new_meteor_dir
   os.system(cmd)

   show_meteor_frames(new_meteor_dir) 



   

def get_days():
   days = []
   files = os.listdir("/mnt/ams2/meteors/")
   for file in files:
      if file[0] == "2":
         # the above line will stop working in 980 years i.e. y3k
         days.append(file)
   return(sorted(days, reverse=True))

def image_equal(im1, im2):
  return ImageChops.difference(im1, im2).getbbox() is None

def rmsdiff(im1, im2):
    #"Calculate the root-mean-square difference between two images"

    h = ImageChops.difference(im1, im2).histogram()

    # calculate rms
    return(math.sqrt(functools.reduce(operator.add, map(lambda h, i: h*(i**2), h, range(256))) / (float(im1.size[0]) * im1.size[1])))

def main():

   form = cgi.FieldStorage()
   act = form.getvalue('act')
   #act = "clip_time" 
   if act == None:
      show_days()
   if act == "show_day":
      day = form.getvalue('day')
      show_day(day)
   if act == "workon":
      meteor = form.getvalue('meteor')
      workon(meteor)
   if act == "clip_time":
      meteor = form.getvalue('meteor')
      start = form.getvalue('start')
      dur = form.getvalue('dur')
      start_mod = form.getvalue('start_mod')
      override = form.getvalue('override')
      if override is None:
         override = 0
      #start = 24
      #start_mod = 2
      #meteor = "/mnt/ams2/meteors/2018-04-12/2018-04-12_05-02-52-cam6.mp4"
      #dur = 5
      clip_time(meteor, start, dur, start_mod,override)

def clip_time(meteor, start, dur, start_mod, override):
   print ("<h1>Deterine meteor event time and make clip</h1>")
   print ("<B>File: </B> " + meteor + "<BR>")
   print ("<B>Start: </B> " + str(start)+ "<BR>")
   print ("<B>Duration: </B> " + str(dur)+ "<BR>")
   print ("<B>Start Mod: </B> " + str(start_mod)+ "<BR>")
   print ("<B>Override: </B> " + str(override)+ "<BR>")

   start = int(start) - int(start_mod)
   trim_file = meteor.replace(".mp4", "-trim.mp4")
   file_exists = Path(trim_file)
   if (file_exists.is_file() and int(override) == 0):
      print ("<div>Trim file already exists, save form below to overwrite existing trim.</div>", override) 
   else:
      cmd = "/home/ams/fireball_camera/ffmpeg-trim.py " + meteor + " " + str(start) + " " + str(dur) + " > /tmp/clipout.txt 2>&1 &"
      print(cmd)
      os.system(cmd)
      
   trim_file = meteor.replace(".mp4", "-trim.mp4")
   start = int(start) + int(start_mod)
   print ("<iframe width=640 height=480 src=" + trim_file + "></iframe>")
   print ("<P><a href=" + trim_file + ">" + trim_file + "</a><br>") 

   print ("<B>To re-clip the event, change the paramaters in the form to adjust the start and end time.</B>")
   print("<form ><input type=hidden name=act value=clip_time>")
   print("<input type=hidden name=meteor value=" + meteor + ">")
   print("<input type=hidden name=override value=1>")
   print("<input type=hidden name=start_mod value=" + str(start_mod) + ">")
   print("Start Time: <input type=text name=start value=" + str(start) + "><BR>")
   print("Duration: <input type=text name=dur value=" + str(dur)+ "><BR>")
   print("<input type=submit value=\"Re-Clip\">")
   print("</form>")

   dump_frames(trim_file)


def workon(meteor):
   print ("<h1>Work on Meteor</h1>" )
   el = meteor.split('/')
   meteor_stack_file = meteor
   meteor_stack_file1 = meteor.replace("-stacked.jpg", "-stacked1-thumb.jpg")
   meteor_stack_file2 = meteor.replace("-stacked.jpg", "-stacked2-thumb.jpg")
   meteor_stack_file3 = meteor.replace("-stacked.jpg", "-stacked3-thumb.jpg")
   meteor_stack_file4 = meteor.replace("-stacked.jpg", "-stacked4-thumb.jpg")
   meteor_stack_file5 = meteor.replace("-stacked.jpg", "-stacked5-thumb.jpg")

   meteor_sd_video_file = meteor.replace("-stacked.jpg", ".mp4")
   meteor_filename = el[-1]
   meteor_filename = meteor_filename.replace("-stacked.jpg", ".mp4")

   print ("<div><span>1 Minute SD Clip:</span><span><a href=" + str(meteor_sd_video_file) + " target=_blank>" + str(meteor_filename) + "</a></span></div>")
   print ("<h2>12 second clip files:</h2>")
   file_time = meteor.split("-", )
   seconds = file_time[6]
   start_mod = seconds
   act_url = "meteors.py?act=clip_time&meteor=" + meteor_sd_video_file + "&start=0&dur=13&start_mod=0"
   print ("<div style=\"float: left\"><a href=" + str(act_url) + " target=_blank><img src=" + str(meteor_stack_file1) + "></a></div>")
   act_url = "meteors.py?act=clip_time&meteor=" + meteor_sd_video_file + "&start=12&dur=13&start_mod=" + str(1)
   print ("<div style=\"float: left\"><a href=" + str(act_url) + " target=_blank><img src=" + str(meteor_stack_file2) + "></a></div>")
   act_url = "meteors.py?act=clip_time&meteor=" + meteor_sd_video_file + "&start=24&dur=14&start_mod=" + str(2)
   print ("<div style=\"float: left\"><a href=" + str(act_url) + " target=_blank><img src=" + str(meteor_stack_file3) + "></a></div>")
   act_url = "meteors.py?act=clip_time&meteor=" + meteor_sd_video_file + "&start=36&dur=15&start_mod=" + str(3)
   print ("<div style=\"float: left\"><a href=" + str(act_url) + " target=_blank><img src=" + str(meteor_stack_file4) + "></a></div>")
   act_url = "meteors.py?act=clip_time&meteor=" + meteor_sd_video_file + "&start=48&dur=16&start_mod=" + str(4)
   print ("<div style=\"float: left\"><a href=" + str(act_url) + " target=_blank><img src=" + str(meteor_stack_file5) + "></a></div>")
   print ("<div style=\"clear: both\"></div>")

   print ("Event Time and Duration")
   print ("Reduce AZ/EL Values")
   print ("Trim Video")
   print ("View SD Video")
   print ("View HD Video")

def show_days():
   days = get_days()
   for day in days:
      show_day(day, 1)
      #print ("<li><A HREF=meteors.py?act=show_day&day=" + day + ">" + day + "</a>")

def show_day(day, batch = 0):
   print ("<h1 style=\"clear: both\">Meteors on " + str(day) + "</h1>")
   meteors = get_meteor_stacks(day)
   for meteor in meteors:
      meteor_thumb = meteor.replace(".jpg", "-thumb.jpg")

      #print ("<div style=\"float:left\"><a href=meteors.py?act=workon&meteor=" + str(meteor) + "><img src=" + meteor_thumb + "></a></div>")
      print ("<div style=\"float:left\"><a href=meteors.py?act=workon&meteor=" + str(meteor) + "><img src=" + meteor_thumb + "></a></div>")
   
main()

#!/usr/bin/python3

import cv2
import os
import sys
from pathlib import Path
import glob
import datetime

hd_dir = "/mnt/ams2/HD/"
tl_dir = "/mnt/ams2/timelapse/"

def video_from_stills(file_list, outfile):
   html = ""
   open_cv_image = cv2.imread(file_list[0],1)
   height , width, chan =  open_cv_image.shape

   # Define the codec and create VideoWriter object
   fourcc = cv2.VideoWriter_fourcc(*'H264')
   out = cv2.VideoWriter(outfile,fourcc, 25, (width,height),1)

   sorted_list = sorted(file_list)
   count = 0
   for filename in sorted_list:
    if count % 1 == 0:
       open_cv_image = cv2.imread(filename,1)
       h , w, c=  open_cv_image.shape
       if h == height and w == width and c == chan:
          print ("adding", filename)
          out.write(open_cv_image)
          html = html + "<img width=480 height=270 src=" + filename + "><BR>"

    count = count + 1
    outhtml = outfile.replace(".avi", ".html")

    htmlout = open(outhtml, "w")
    htmlout.write(html)
    htmlout.close()

def convert_filename_to_date_cam(file):
   el = file.split("/")
   filename = el[-1]
   f_date, f_time_cam = filename.split("_")
   el = f_time_cam.split("-")
   if len(el) == 4:
     f_h, f_m, f_s, f_cam = f_time_cam.split("-")
     f_cam = f_cam.replace(".mp4", "")
     f_date_str = f_date + " " + f_h + ":" + f_m + ":" + f_s
     f_datetime = datetime.datetime.strptime(f_date_str, "%Y-%m-%d %H:%M:%S")
   return(f_datetime, f_cam, f_date, f_h, f_m, f_s)


def extract_image_from_video():
   for hd_file in sorted((glob.glob(hd_dir + "*.mp4")), reverse=True):
      print("HD FILE", hd_file)
      tl_file = hd_file.replace("HD", "timelapse")
      tl_file = tl_file.replace("mp4", "jpg")
      file_exists = Path(tl_file)
      if (file_exists.is_file()):
         print("Already did: ", tl_file)
      else:
         cmd = "ffmpeg -ss 00:00:01 -i " + hd_file + " -vframes 1 -vf scale=640:360 " + tl_file
         os.system(cmd)

def purge_old(): 
   now_datetime = datetime.datetime.now()
   file_list = [] 
   c = 0
   cmd = ""
   for tl_file in sorted((glob.glob(tl_dir + "*.*"))):
      (f_datetime, f_cam, f_date, f_h, f_m, f_s) = convert_filename_to_date_cam(tl_file)
      tdelta = now_datetime -f_datetime 
      alpha = float(tdelta.total_seconds()/86400   )
      if alpha > 4:
         cmd = "rm " + tl_file
         os.system(cmd)
      if c % 1000 == 0:
         print (cmd)
      c = c + 1

def make_time_lapse_video(start, end, cam_num): 
  
   file_list = [] 
   start_datetime = datetime.datetime.strptime(start, "%Y-%m-%d_%H:%M:%S")
   end_datetime = datetime.datetime.strptime(end, "%Y-%m-%d_%H:%M:%S")
   print("Timelapse for camera : ", cam_num, start_datetime, end_datetime)
   for tl_file in sorted((glob.glob(tl_dir + "*cam" + cam_num + "*.jpg"))):
      (f_datetime, f_cam, f_date, f_h, f_m, f_s) = convert_filename_to_date_cam(tl_file)
      if start_datetime <= f_datetime <= end_datetime:
         print (tl_file)
         file_list.append(tl_file)
   jj = start.split("_");
   outvideo = jj[0] + "-" + str(cam_num) + ".avi"
   video_from_stills(file_list, "/mnt/ams2/timelapse_videos/" + outvideo)


act = sys.argv[1]

if act == "extract":
   extract_image_from_video()
if act == "purge":
   purge_old()

if act == "tl":
   start_datetime = sys.argv[2]
   end_datetime = sys.argv[3]
   cam_num = sys.argv[4]
   make_time_lapse_video(start_datetime, end_datetime, cam_num)

#!/usr/bin/python3 

import sys
import glob
import datetime
import os

def ffmpeg_cat (file1, file2, outfile):
   cat_file = "/tmp/cat_files.txt"
   fp = open(cat_file, "w")
   fp.write("file '" + file1 + "'\n")
   fp.write("file '" + file2 + "'\n")
   fp.close()
   cmd = "ffmpeg -f concat -safe 0 -i " + cat_file + " -c copy " + outfile 
   print(cmd)
   os.system(cmd)

def ffmpeg_trim (filename, trim_start_sec, dur_sec, out_file_suffix):
   #ffmpeg -i /mnt/ams2/meteors/2018-09-20/2018-09-20_22-20-05-cam5-hd.mp4 -ss 00:00:46 -t 00:00:06 -c copy /mnt/ams2/meteors/2018-09-20/2018-09-20_22-20-05-cam5-hd-trim.mp4 

   outfile = filename.replace(".mp4", out_file_suffix + ".mp4") 
   cmd = "ffmpeg -i " + filename + " -y -ss 00:00:" + trim_start_sec + " -t 00:00:" + dur_sec + " -c copy " + outfile
   print (cmd)
   os.system(cmd)
   return(outfile)

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

def find_hd_file(sd_file):
   hd_dir = "/mnt/ams2/HD";
   sd_datetime, sd_cam, sd_date, sd_h, sd_m, sd_s = convert_filename_to_date_cam(sd_file)
   print ("SD File", sd_file)
   print ("SD Datetime ", sd_datetime)
   print ("SD Cam", sd_cam)

   hd_wild_card = "/mnt/ams2/HD/" + sd_date + "_" + sd_h + "-" + sd_m + "*" + sd_cam + ".mp4"
   print ("HD Wildcard: ", hd_wild_card)

   for hd_file in (glob.glob(hd_wild_card)):
      print("HD FILE", hd_file)
      hd_datetime, hd_cam, hd_date, hd_h, hd_m, hd_s = convert_filename_to_date_cam(hd_file)
   time_offset = sd_datetime - hd_datetime
   print ("Time offset: ", sd_datetime - hd_datetime)
   tos_ts = time_offset.total_seconds()

   # trim the hd file ss= time offset to end of file (60 - time offset) and put in temp1
   if int(tos_ts) >= 0:
      hd_file1 = ffmpeg_trim(hd_file, str(tos_ts), str(60 - int(tos_ts)), "-sd_linked.mp4")

   # then find the next hd_file (increment datetime + 1 minute, determine/find filename and then trim from beginning of file with duration of time offset into temp2
   next_hd_datetime = hd_datetime + datetime.timedelta(0,60)
   next_hd_wildcard = hd_dir + "/" + next_hd_datetime.strftime("%Y-%m-%d_%H-%M") + "*" + hd_cam + ".mp4"
   print ("NEXT HD WILDCARD", next_hd_wildcard)
   # cat temp1 and temp2 to get the sd_mirrored HD file. 
   for next_hd_file in (glob.glob(next_hd_wildcard)):
      print("NEXT HD FILE", hd_file)
      next_hd_datetime, next_hd_cam, next_hd_date, next_hd_h, next_hd_m, next_hd_s = convert_filename_to_date_cam(next_hd_file)

   # trim the next HD file from the start to the original offset
   hd_file2 = ffmpeg_trim(next_hd_file, str(0), str(int(tos_ts)), "-sd_linked")
   hd_outfile = hd_dir + "/" + str(sd_date) + "_" + sd_h + "-" + sd_m + "-" + sd_s + "-" + sd_cam + "-HD-sync.mp4"
   ffmpeg_cat(hd_file1, hd_file2, hd_outfile)    


sd_file = sys.argv[1]
hd_file = find_hd_file(sd_file)

#ffmpeg_trim("/mnt/ams2/HD/2018-09-27_09-37-01-cam2.mp4", "10", "10", "-test-trim")

#/mnt/ams2/meteors/2018-09-27/2018-09-27_09-37-20-cam2.mp4
#/mnt/ams2/HD/2018-09-27_09-37-01-cam2.mp4

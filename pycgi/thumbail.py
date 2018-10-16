#!/usr/bin/python3 

import sys,os
import glob
from PIL import Image
from pathlib import Path

#dir = sys.argv[1]
#match_str = sys.argv[2]

def get_days():
   days = []
   files = os.listdir("/mnt/ams2/meteors/")
   for file in files:
      if file[0] == "2":
         # the above line will stop working in 980 years i.e. y3k
         days.append(file)
   return(sorted(days, reverse=True))

def check_stacks(dir):
   match_str = "stacked.jpg"
   print (dir + "/*" + match_str)
   stacks = sorted((glob.glob(dir + "/*" + match_str)))
   for stack_file in stacks:
      stack1 = stack_file.replace("stacked.jpg", "stacked1.jpg")
      meteor_video = stack_file.replace("-stacked.jpg", ".mp4")
      file_exists = Path(stack1)
      if (file_exists.is_file()):
         print ("stack exists", stack1)
      else: 
         cmd = "/home/ams/fireball_camera/fast_frames5.py " + meteor_video
         print ("need to remake stacks for this meteor?")
         print (cmd)
         os.system(cmd)


def thumbnail_dir(dir, match_str):
   size = 384,216 
   print ("Doing " + str(dir))
   work_files = [] 
   all_files = sorted(glob.glob(dir + "/*" + match_str))
   for infile in all_files:
      if "thumb" in infile:
         print ("Already done.")
      else:
         work_files.append(infile)

   for infile in sorted(work_files):
      outfile = infile.replace(".jpg", "-thumb.jpg")
      file_exists = Path(outfile)
      if (file_exists.is_file()):
         print ("Already Done")
      else:
         try:
            im = Image.open(infile)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(outfile, "JPEG")
         except:
            print ("Failed to convert:", infile)

def check_all():
   days = get_days()
   match_str = ".jpg"
   for day in days:
      check_stacks("/mnt/ams2/meteors/" + day)
      print(day)
      thumbnail_dir("/mnt/ams2/meteors/" + day + "/", match_str)

check_all()



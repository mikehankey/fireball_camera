#!/usr/bin/python3

import subprocess
import glob
import os
from pathlib import Path

proc_dir = "/mnt/ams2/SD/proc/*"

def parse_date (this_file):

   el = this_file.split("/")
   file_name = el[-1]
   file_name = file_name.replace("_", "-")
   file_name = file_name.replace(".", "-")
   fnel = file_name.split("-")
   #print("FILE:", file_name, len(fnel))
   if len(fnel) == 11:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype,fnum,fst,xext = fnel
   if len(fnel) == 10:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype,fnum,xext = fnel
   if len(fnel) == 9:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype, xext = fnel
   if len(fnel) == 8:
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, xext = fnel

   cam_num = xcam_num.replace("cam", "")

   date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
   capture_date = date_str
   return(cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec)


def check_running():
   cmd = "ps -aux |grep \"tag-runner.py\" | grep -v grep | wc -l"
   print(cmd)
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   return(int(output))


def count_images(check_dir):
   jobs = []
   el = check_dir.split("/")
   proc_date = el[-1]
   mp4s = glob.glob(check_dir + "/*.mp4")
   print ("Total MP4s:", len(mp4s))

   stacks = glob.glob(check_dir + "/*stacked.jpg")
   print ("Total Stacks:", len(stacks))

   blends = glob.glob(check_dir + "/*blend.jpg")
   print ("Total Blends:", len(blends))

   diffs = glob.glob(check_dir + "/*diff.jpg")
   print ("Total Diffs:", len(diffs))

   if len(blends) != len(stacks):
      for i in range(1,7):
         job = "./master-stacks.py " + str(proc_date) + " " + str(i)
         jobs.append(job)

   if len(diffs) != len(stacks):
      for i in range(1,7):
         job = "./diff-stacks.py " + proc_date + " " + str(i)
         jobs.append(job)
  
   return(jobs) 

def main():
   running = check_running()
   if running > 2:
      print("Already running. Abort.", running)
      exit()
   all_jobs = []
   for filename in (glob.glob(proc_dir)):
      for cam_num in range(1,7):
         tag_file = filename + "/" + "tags-cam" + str(cam_num) + ".txt"
         file_exists = Path(tag_file)
         if (file_exists.is_file()):
            print("Tag File found.", tag_file)
            process_tag_file(tag_file)

def process_tag_file(tag_file):
   # for each tag, if it is meteor run PV on the file if it hasn't already been run. 
   # if a meteor is detected the trim file is created and copied, 
   # but if the trim file doesn't exist then the auto detect failed. In this case just copy entire clip 
   # if it is a plane, just copy the stack image to the plane learning dir
   # if it is a sat, just copy the stack image to the sat dir
   fp = open(tag_file, "r")
   for line in fp:
      line = line.replace("\n", "")
      act, tag, file = line.split(",")
      if act == 'add':
         if tag == 'meteor':
            (cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = parse_date(file)
            video_file = file
            cmd = "./PV.py " + video_file + " " + cam_num       
#/mnt/ams2/SD/proc/2018-05-02/2018-05-02_09-10-02-cam4-report.txt
            rpt_file = file.replace(".mp4", "-report.txt")
            file_exists = Path(rpt_file)
            if (file_exists.is_file()):
               print ("already did this.")
            else:
               print (act, tag, file, cam_num, date_str)
               print(cmd)
               os.system(cmd)
         stack_file = file.replace(".mp4", "-stacked.jpg")
         el = stack_file.split("/")
         stack_fn = el[-1]
         if tag == 'plane':
            new_stack_file = "/mnt/ams2/saved/planes/" + stack_fn
            file_exists = Path(new_stack_file)
            if (file_exists.is_file() == False):
               cmd = "cp " + stack_file + " " + new_stack_file
               os.system(cmd)

         if tag == 'sat':
            new_stack_file = "/mnt/ams2/saved/sats/" + stack_fn
            file_exists = Path(new_stack_file)
            if (file_exists.is_file() == False):
               cmd = "cp " + stack_file + " " + new_stack_file
               os.system(cmd)

         if tag == 'other' :
            new_stack_file = "/mnt/ams2/saved/other/" + stack_fn
            file_exists = Path(new_stack_file)
            if (file_exists.is_file() == False):
               cmd = "cp " + stack_file + " " + new_stack_file
               os.system(cmd)
         if tag == 'interesting' :
            new_stack_file = "/mnt/ams2/saved/interesting/" + stack_fn
            file_exists = Path(new_stack_file)
            if (file_exists.is_file() == False):
               cmd = "cp " + stack_file + " " + new_stack_file
               os.system(cmd)

main()

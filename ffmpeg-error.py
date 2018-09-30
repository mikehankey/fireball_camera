#!/usr/bin/python3 
import os
import sys
import subprocess


def check_live_errors(cam_num):
   cmd = "find /mnt/ams2/SD -mmin -2 |grep mp4 | grep -v proc | grep cam" + str(cam_num) 
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output.replace("\n", "")
   files = output.split("\n")
   #print(files)
   check_vid_errors(files[0])

def check_vid_errors(file):
   err_file = file.replace(".mp4", ".err")
   cmd = "ffmpeg -v error -i " + file + " -f null - > " + err_file + " 2>&1"
   os.system(cmd)
   cmd = "cat " + err_file + " | wc -l"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = output.replace("\n", "")
   print(cmd)
   print(file + " " + output + " errors")


file = sys.argv[1]

check_live_errors(1)

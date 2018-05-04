#!/usr/bin/python

import subprocess
import glob
import os

proc_dir = "/mnt/ams2/SD/proc/*"

def check_running():
   cmd = "ps -aux |grep \"stack-runner.py\" | grep -v grep | wc -l"
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
      print(filename)
      jobs = count_images(filename)
      all_jobs.append((jobs))

   for job_group in all_jobs:
      for job in job_group:
         print(job)
         os.system(job)


main()

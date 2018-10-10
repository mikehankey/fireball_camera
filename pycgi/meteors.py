#!/usr/bin/python3

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


print ("Content-type: text/html\n\n")

def get_meteor_stacks(day):
   meteors = []

   files = glob.glob("/mnt/ams2/meteors/" + str(day) + "/*stacked.jpg")
   for file in files:
      meteors.append(file)
   return(sorted(meteors, reverse=True))

def get_days():
   days = []
   files = os.listdir("/mnt/ams2/meteors/")
   for file in files:
      if file[0] == "2":
         # the above line will stop working in 980 years i.e. y3k
         days.append(file)
   return(sorted(days, reverse=True))

def main():

   form = cgi.FieldStorage()
   act = form.getvalue('act')
   if act == None:
      show_days()
   if act == "show_day":
      day = form.getvalue('day')

      show_day(day)

def show_days():
   days = get_days()
   for day in days:
      print ("<li><A HREF=meteors.py?act=show_day&day=" + day + ">" + day + "</a>")

def show_day(day):
   print ("<h1>Meteors on " + str(day) + "</h1>")
   meteors = get_meteor_stacks(day)
   for meteor in meteors:
      meteor_thumb = meteor.replace(".jpg", "-thumb.jpg")
      print ("<div style=\"float:left\"><img src=" + meteor_thumb + "></div>")
   

main()

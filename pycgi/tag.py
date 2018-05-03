#!/usr/bin/python3
import glob
import subprocess
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"

def parse_date (this_file):

   el = this_file.split("/")
   file_name = el[-1]
   file_name = file_name.replace("_", "-")
   file_name = file_name.replace(".", "-")
   xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, xext = file_name.split("-")
   cam_num = xcam_num.replace("cam", "")

   date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
   capture_date = date_str
   return(cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec)

print ("Content-type: text/html\n\n")
form = cgi.FieldStorage()
file = form.getvalue('file')
status = form.getvalue('status')
tag = form.getvalue('tag')
#file="/mnt/ams2/SD/proc/2018-05-02/2018-05-02_09-10-02-cam4.mp4"
#status="false"
#tag="meteor"

(cam_num, date_str, xyear, xmonth, xday, xhour, xmin, xsec) = parse_date(file)

if status == "true":
   act = "remove"
else:
   act = "add"

el = file.split("/");
home_dir = file.replace(el[-1], "")
if " " in home_dir or "|" in home_dir or ">" in home_dir:
   exit()

tag_file = home_dir + "tags-cam" + cam_num + ".txt"

tags = open(tag_file, "a")
tags.write(act+ "," + tag + "," + file + "\n")
tags.close()

print (file, status, tag)

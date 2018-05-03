#!/usr/bin/python3
from collections import defaultdict
import glob
import subprocess 
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"
from pathlib import Path

#cgi.enable()
print ("Content-type: text/html\n\n")
print (" <style> .active { background: #ff0000; } .inactive { background: #ffffff; } </style>")

def get_days():
   days = []
   files = os.listdir(video_dir + "proc/")
   for file in files:
      if file[0] == "2":
         # the above line will stop working in 980 years i.e. y3k
         days.append(file)
   return(sorted(days))

def make_archive_links():
   days = get_days()
   d = 0
   html = ""
   for day in days:
      html = html + "<b>" + day + "</b> "
      for cn in range(1,7):
         if cn != 1:
            html = html + " - "
         html = html + "<a href=archive-side.py?cmd=browse_day&day=" + day + "&cam_num=" + str(cn) + ">" + str(cn) + "</a>" + "\n"
      html = html + "<P>"
      d = d + 1
   return(html)

def get_files_for_day_cam(day, cam):
   if 1 <= int(cam) <= 6 and len(day) == 10:
      good = 1
   else: 
      print("Bad.")
      exit()
      
   glob_dir = video_dir + "proc/" + day + "/*cam" + str(cam) + "*.mp4"
   files = glob.glob(glob_dir)
   return(sorted(files))

def mark_tag(word, tags):
   if word in tags:
      return("active")
   else:
      return("inactive")


def browse_day(day, cam):
   form = cgi.FieldStorage()
   debug = form.getvalue('debug')
   print("<script src=/pycgi/tag_pic.js></script>")
   print ("<h2>Browse Day</h2>")
   report_file = "/mnt/ams2/SD/proc/" + str(day) + "/" + str(day) + "-cam" + str(cam) + "-report.txt"
   files = get_files_for_day_cam(day, cam)
   file_dict = defaultdict()
   for file in files:
      file_dict[file] = {}
      file_dict[file]['tags'] = ""

   tag_file = "/mnt/ams2/SD/proc/" + str(day) + "/" + "tags-cam" + str(cam) + ".txt"
   file_exists = Path(tag_file)
   if (file_exists.is_file()):
      file_dict = parse_tags(tag_file, file_dict) 

   for file in files:
      jpg = file.replace(".mp4", "-stacked.jpg") 
      blend = file.replace(".mp4", "-blend.jpg") 
      diff = file.replace(".mp4", "-diff.jpg") 
      tags = file_dict[file]['tags']
      print ("<table><tr><td><a href=" + file + "><img src=" + jpg + "></a><BR>")
      cls = mark_tag("meteor", tags)
      print ("<input type=button name=tag value=\"meteor\" onclick=\"javascript:tag_pic('" + file + "', 'meteor', event);\" class='" + cls + "'>")
      cls = mark_tag("plane", tags)
      print ("<input type=button name=tag value=\"plane\" onclick=\"javascript:tag_pic('" + file + "', 'plane', event);\" class='" + cls + "'>")
      cls = mark_tag("sat", tags)
      print ("<input type=button name=tag value=\"sat\" onclick=\"javascript:tag_pic('" + file + "', 'sat', event);\" class='" + cls + "'>")
      cls = mark_tag("cloud", tags)
      print ("<input type=button name=tag value=\"cloud\" onclick=\"javascript:tag_pic('" + file + "', 'cloud', event);\" class='" + cls + "'>")
      cls = mark_tag("notsure", tags)
      print ("<input type=button name=tag value=\"notsure\" onclick=\"javascript:tag_pic('" + file + "', 'notsure', event);\" class='" + cls + "'>")
      cls = mark_tag("interesting", tags)
      print ("<input type=button name=tag value=\"interesting\" onclick=\"javascript:tag_pic('" + file + "', 'interesting', event);\" class='" + cls + "'>")
      cls = mark_tag("other", tags)
      print ("<input type=button name=tag value=\"other\" onclick=\"javascript:tag_pic('" + file + "', 'other', event);\" class='" + cls + "'>")



      print("</td><td>")
      if debug is not None:
         print("<img src=" + blend + "></a><BR></td><td><img src=" + diff + "></a><BR> </td></tr></table> ")
      else:
         print("</td><td></td></tr></table> ")


def main():
   form = cgi.FieldStorage()
   cam_num = form.getvalue('cam_num')
   day = form.getvalue('day')

   cmd = form.getvalue('cmd')
   # for testn
   #cmd = "browse_day"
   #day = "2018-05-02"
   #cam_num = 1

   archive_links = make_archive_links()

   if cmd is None:
      print ("<h2>View Archive</h2>")
      print("Select a day and camera to browse.<P>")
      print(archive_links)
   if cmd == "browse_day":
    
      browse_day(day, cam_num)  

def parse_tags(tag_file, file_dict):
   fp = open(tag_file, "r");
   for line in fp:
      line = line.replace("\n", "")
      (cmd, tag, file) = line.split(",")
    #  if cmd == 'add':
      file_dict[file]['tags'] = file_dict[file]['tags'] + "," + tag
    #  else:
    #     file_dict[file]['tags'].replace(tag+",", "")
   return(file_dict)   

main()



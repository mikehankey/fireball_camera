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

#cgi.enable()
print ("Content-type: text/html\n\n")
print (" <style> .active { background: #ff0000; } .inactive { background: #ffffff; } body { background-color: #000000; color: #ffffff } </style>")

def get_days():
   days = []
   files = os.listdir(video_dir + "proc/")
   for file in files:
      if file[0] == "2":
         # the above line will stop working in 980 years i.e. y3k
         days.append(file)
   return(sorted(days, reverse=True))

def load_scan_file(day, cam_num):
   #/mnt/ams2/SD/proc/2018-05-10/cam5.txt
   scan_file = video_dir + "proc/" + day + "/" + "cam" + str(cam_num) + ".txt" 
   img_dict = dict()
   file_exists = Path(scan_file)
   od = 0
   if (file_exists.is_file()):
      sfp = open(scan_file, "r")
      for line in sfp:
         (img_file, status_desc, hit) = line.split(",") 
         img_dict[img_file] = {}
         img_dict[img_file]['status_desc'] = status_desc
         img_dict[img_file]['hit'] = hit 
         if int(hit) == 1:
            od = od + 1
          
   else:
      print ("Scan file does not exists.", scan_file)
   
   return(img_dict, od)

def make_archive_links():
   days = get_days()
   d = 0
   html = ""
   for day in days:
      html = html + "<h2>" + day + "</h2> "
      for cn in range(1,7):
         #if cn != 1:
         #   html = html + " - "
         rand_num = random.randint(1,10000)
         #master_stack_file = "/mnt/ams2/SD/proc/" + day + "/" + day + "-cam" + str(cn) + "-master_stack.jpg?" + str(rand_num)
         master_stack_file = "/mnt/ams2/SD/proc/" + day + "/"  + "cam" + str(cn) + "-master_stack.jpg?" + str(rand_num)
         #master_stack_img = "<img alt='cam" + str(cn) + "' onmouseover='bigImg(this)' onmouseout='normalImg(this)' width=320 height=240 src='" + master_stack_file + "'>"
         master_stack_img = "<img alt='cam" + str(cn) + "' onmouseover='normalImg(this)' onmouseout='normalImg(this)' width=320 height=240 src='" + master_stack_file + "'>"
         html = html + "<a href=archive-side.py?cmd=browse_day&day=" + day + "&cam_num=" + str(cn) + ">" + master_stack_img + "</a>" + "\n"
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
   print ("<h2>Browse Day " + str(day) + " Cam " + str(cam) + "</h2>")
   report_file = "/mnt/ams2/SD/proc/" + str(day) + "/" + str(day) + "-cam" + str(cam) + "-report.txt"
   img_dict, od = load_scan_file(day, cam)
   files = get_files_for_day_cam(day, cam)
   file_dict = defaultdict()
   print(str(len(files)) + " total files <BR>")
   print(str(od) + " objects auto detected<BR>")
   for file in files:
      file_dict[file] = {}
      file_dict[file]['tags'] = ""

   tag_file = "/mnt/ams2/SD/proc/" + str(day) + "/" + "tags-cam" + str(cam) + ".txt"
   file_exists = Path(tag_file)
   if (file_exists.is_file()):
      file_dict = parse_tags(tag_file, file_dict) 
   count = 0
   for file in files:
      jpg = file.replace(".mp4", "-stacked.jpg") 
      blend = file.replace(".mp4", "-blend.jpg") 
      #diff = file.replace(".mp4", "-diff.jpg") 
      diff = file.replace(".mp4", "-objects.jpg") 
      if jpg in img_dict:
         hit = img_dict[jpg]['hit']   
         status_desc = img_dict[jpg]['status_desc']   
      else: 
         hit = 0 
         status_desc = "rejected for brightness" 
      tags = file_dict[file]['tags']
      print ("<div class='divTable'>")
      print ("<div class='divTableBody'>")
      print ("<div class='divTableRow'>")
      if int(hit) == 1:
         print ("<div class='divTableCellDetect'>")
      else:
         print ("<div class='divTableCell'>")
      print ("<a href=" + file + " onmouseover=\"document.img" + str(count) + ".src='" + diff + "'\" onmouseout=\"document.img" + str(count) + ".src='" + jpg + "'\"><img name='img" + str(count) + "' src=" + jpg + "></a></div>")
      print ("<div class='divTableCell'>") 

      # start the button area here
      print ("<div class='divTable'>")
      print ("<div class='divTableBody'>")
      print ("<div class='divTableRow'>")
      print ("<div class='divTableCell'>")

      cls = mark_tag("meteor", tags)
      print ("<input type=button name=tag value=\"   meteor  \" onclick=\"javascript:tag_pic('" + file + "', 'meteor', event);\" class='" + cls + "'>")
      print ("</div></div>")
      print ("<div class='divTableRow'>")
      print ("<div class='divTableCell'>")

      cls = mark_tag("plane", tags)
      print ("<input type=button name=tag value=\"    plane   \" onclick=\"javascript:tag_pic('" + file + "', 'plane', event);\" class='" + cls + "'>")
      print ("</div></div>")
      print ("<div class='divTableRow'>")
      print ("<div class='divTableCell'>")

      cls = mark_tag("sat", tags)
      print ("<input type=button name=tag value=\"    sat      \" onclick=\"javascript:tag_pic('" + file + "', 'sat', event);\" class='" + cls + "'>")
      print ("</div></div>")
      print ("<div class='divTableRow'>")
      print ("<div class='divTableCell'>")

      cls = mark_tag("cloud", tags)
      print ("<input type=button name=tag value=\"   cloud   \" onclick=\"javascript:tag_pic('" + file + "', 'cloud', event);\" class='" + cls + "'>")
      print ("</div></div>")
      print ("<div class='divTableRow'>")
      print ("<div class='divTableCell'>")

      cls = mark_tag("notsure", tags)
      print ("<input type=button name=tag value=\"  notsure \" onclick=\"javascript:tag_pic('" + file + "', 'notsure', event);\" class='" + cls + "'>")
      print ("</div></div>")
      print ("<div class='divTableRow'>")
      print ("<div class='divTableCell'>")


      cls = mark_tag("interesting", tags)
      print ("<input type=button name=tag value=\"interesting\" onclick=\"javascript:tag_pic('" + file + "', 'interesting', event);\" class='" + cls + "'>")
      print ("</div></div>")
      print ("<div class='divTableRow'>")
      print ("<div class='divTableCell'>")



      cls = mark_tag("other", tags)
      print ("<input type=button name=tag value=\"   other    \" onclick=\"javascript:tag_pic('" + file + "', 'other', event);\" class='" + cls + "'>")
      print ("</div></div>")
      print ("</div>")
      print ("</div>")

      print (str(hit) + "-" + status_desc)
      print ("</div></div></div></div><P>")
      count = count + 1

      #print("</td><td>")
      if debug is not None:
         print("<img src=" + blend + "></a><BR></td><td><img src=" + diff + "></a><BR> </td></tr></table> ")
      #else:
      #   print("</td><td></td></tr></table> ")


def main():
   rand_num = random.randint(1,10000)
   print ("<link rel='stylesheet' href='div_table.css?" + str(rand_num) + "'>")
   print("<script src='/pycgi/big-little-image.js'></script>")

   form = cgi.FieldStorage()
   cam_num = form.getvalue('cam_num')
   day = form.getvalue('day')

   cmd = form.getvalue('cmd')
   # for testn
   #cmd = "browse_day"
   #day = "2018-05-10"
   #cam_num = 5


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
      if cmd == 'add':
         file_dict[file]['tags'] = file_dict[file]['tags'] + "," + tag
      else:
         file_dict[file]['tags'] = file_dict[file]['tags'].replace(tag, "")
   return(file_dict)   

main()



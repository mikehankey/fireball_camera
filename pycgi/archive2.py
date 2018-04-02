#!/usr/bin/python3
import glob
import subprocess 
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"

#cgi.enable()
print ("Content-type: text/html\n\n")


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
         html = html + "<a href=archive2.py?cmd=browse_day&day=" + day + "&cam_num=" + str(cn) + ">" + str(cn) + "</a>" + "\n"
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

def browse_day(day, cam):
   print ("<h2>Browse Day</h2>")
   report_file = "/mnt/ams2/SD/proc/" + str(day) + "/" + str(day) + "-cam" + str(cam) + "-report.txt"
   rpts = open(report_file, "r")
   files = get_files_for_day_cam(day, cam)
   #for file in files:
   for line in rpts:
      file, lg, op, bc = line.split(",")
      jpg = file.replace(".mp4", "-stacked.jpg") 
      if int(lg) > 0 or int(op) > 3 or int(bc) > 0:
         print ("<a href=clip_detail.py?file=" + file + "&day=" +str(day) + "&cam=" +str(cam) + "><img src=" + jpg + "></a><BR>")
      else:
         print ("<a href=" + file + "><img width=320 height=240 src=" + jpg + "></a><BR>")


def main():
   form = cgi.FieldStorage()
   cam_num = form.getvalue('cam_num')
   day = form.getvalue('day')

   cmd = form.getvalue('cmd')
   #cmd = "browse_day"
   #day = "2018-03-06"
   #cam_num = 1

   archive_links = make_archive_links()

   if cmd is None:
      print ("<h2>View Archive</h2>")
      print("Select a day and camera to browse.<P>")
      print(archive_links)
   if cmd == "browse_day":
    
      browse_day(day, cam_num)  


main()


#if cmd is None:
#   days = get_days()
   #scmd = "find /mnt/ams2/SD/" + str(cam_num) + "/time_lapse/ | grep " + str(sdate) 
   #output = subprocess.check_output(scmd, shell=True).decode("utf-8")
#   #files = output.split("\n")
#   report_file = "/mnt/ams2/SD/" + str(cam_num) + "/time_lapse/" + str(sdate) + ".txt"
#   rpts = open(report_file, "r")
#   last_sum_diff = 0 
#   for line in rpts:
#      line = line.replace("\n", "")
#      file,hit,sum_diff = line.split(",")
#      if int(last_sum_diff) > 0 and (int(sum_diff) / int(last_sum_diff) > 1.5):
#         hit = 1
#      if int(hit) == 0:
#         style = "style='opacity: 0.5'"
#      else:
#         style = ""
#      print ("<a target=_blank href=archive.py?cmd=vid&file=" + str(file) + "&cam_num=" + str(cam_num) + "><img "+ style + " src=/mnt/ams2/SD/" + cam_num + "/time_lapse/" + str(file) + "></a>")
#      last_sum_diff = int(sum_diff)
#
#if cmd == "vid":
#   file = form.getvalue('file')
#   el = file.split("/")
#   fn = el[-1]
#   tr = fn.split("cam")
#   sdate = tr[0]
#   scmd = "find ../mnt/ams2/SD/" + str(cam_num) + "/ | grep " + str(sdate) + " |grep mp4"
#   output = subprocess.check_output(scmd, shell=True).decode("utf-8")
#   video = output.split("\n")
#  # print ("<BR>" + output)
#   print ("Location: " + str(video[0]) + "\n\n")
#
#
#
#

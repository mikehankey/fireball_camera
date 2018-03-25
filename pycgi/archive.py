#!/usr/bin/python3
import subprocess 
import cgi
import cgitb

video_dir = "/mnt/ams2/"

#cgi.enable()
form = cgi.FieldStorage()

cam_num = form.getvalue('cam_num')
sdate = form.getvalue('date')
cmd = form.getvalue('cmd')


if cmd is None:
   print ("Content-type: text/html\n\n")
   print ("<h2>View Archive</h2>")

   #scmd = "find /mnt/ams2/SD/" + str(cam_num) + "/time_lapse/ | grep " + str(sdate) 
   #output = subprocess.check_output(scmd, shell=True).decode("utf-8")
   #files = output.split("\n")
   report_file = "/mnt/ams2/SD/" + str(cam_num) + "/time_lapse/" + str(sdate) + ".txt"
   rpts = open(report_file, "r")
   last_sum_diff = 0 
   for line in rpts:
      line = line.replace("\n", "")
      file,hit,sum_diff = line.split(",")
      if int(last_sum_diff) > 0 and (int(sum_diff) / int(last_sum_diff) > 1.5):
         hit = 1
      if int(hit) == 0:
         style = "style='opacity: 0.5'"
      else:
         style = ""
      print ("<a target=_blank href=archive.py?cmd=vid&file=" + str(file) + "&cam_num=" + str(cam_num) + "><img "+ style + " src=/mnt/ams2/SD/" + cam_num + "/time_lapse/" + str(file) + "></a>")
      last_sum_diff = int(sum_diff)

if cmd == "vid":
   file = form.getvalue('file')
   el = file.split("/")
   fn = el[-1]
   tr = fn.split("cam")
   sdate = tr[0]
   scmd = "find ../mnt/ams2/SD/" + str(cam_num) + "/ | grep " + str(sdate) + " |grep mp4"
   output = subprocess.check_output(scmd, shell=True).decode("utf-8")
   video = output.split("\n")
  # print ("<BR>" + output)
   print ("Location: " + str(video[0]) + "\n\n")





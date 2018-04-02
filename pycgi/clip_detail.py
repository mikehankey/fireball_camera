#!/usr/bin/python3
import glob
import subprocess
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"

#cgi.enable()
print ("Content-type: text/html\n\n")
form = cgi.FieldStorage()
day = form.getvalue('day')
cmd = form.getvalue('cmd')
cam = form.getvalue('cam')
file = form.getvalue('file')

#file = "/mnt/ams2/SD/proc/2018-03-24/2018-03-24-00-02-03-cam6-stacked.jpg"
#day = "2018-03-24"
#cam = "6"

el = file.split("/")
fn = el[-1]
sfn = fn.replace("stacked.jpg", "stack-report.txt")
vrf = fn.replace("stacked.jpg", "report.txt")
video_file = file.replace("-stacked.jpg", ".mp4")
stack_report = "/mnt/ams2/SD/proc/" + str(day) + "/" + sfn
video_report = "/mnt/ams2/SD/proc/" + str(day) + "/" + vrf
#print(stack_report + "<BR>")
rpt = open(stack_report, "r")
vrpt = open(video_report, "r")

for line in rpt:
   #print (line + "<BR>")
   exec(line)
for line in vrpt:
   #print (line + "<BR>")
   exec(line)

print ("<B>Video File:</B>" + orig_video_file + "<br>")
print ("<iframe src=" + video_file + " width=640 height=480></iframe><br>")
print ("<TABLE>")
print ("<tr><td valign=top>")
print ("<B>Points:</B>" )
print ("<table border=1>")
print ("<tr><td>X</td><td>Y</td><td>W</td><td>H</td></tr>")
for x,y,w,h in points:
   print ("<tr><td>" + str(x) + "</td><td>" + str(y) + "</td><td>" + str(w) + "</td><td>" + str(h) + "</td></tr>")
print ("</table>")
print ("</td><td valign=top>")

print ("<B>Stars:</B>" )
print ("<table border=1>")
print ("<tr><td>X</td><td>Y</td><td>W</td><td>H</td></tr>")
for x,y,w,h in stars:
   print ("<tr><td>" + str(x) + "</td><td>" + str(y) + "</td><td>" + str(w) + "</td><td>" + str(h) + "</td></tr>")
print ("</table>")
print ("</td><td valign=top>")

print ("<B>Object Points:</B>" )
print ("<table border=1>")
print ("<tr><td>X</td><td>Y</td><td>W</td><td>H</td></tr>")
for x,y,w,h in obj_points:
   print ("<tr><td>" + str(x) + "</td><td>" + str(y) + "</td><td>" + str(w) + "</td><td>" + str(h) + "</td></tr>")
print ("</table>")
print ("</td><td valign=top>")

print ("<B>Big Objects:</B>" )
print ("<table border=1>")
print ("<tr><td>X</td><td>Y</td><td>W</td><td>H</td></tr>")
for x,y,w,h in big_cnts:
   print ("<tr><td>" + str(x) + "</td><td>" + str(y) + "</td><td>" + str(w) + "</td><td>" + str(h) + "</td></tr>")
print ("</table>")
print ("</td></tr>")
print ("</table>")

print ("<B>Frame Count:</B> " + str(frame_count) + "<br>")
print ("<B>FPS:</B> " + str(fps) + "<br>")
print ("<B>Total Motion:</B> " + str(total_motion) + "<br>")
print ("<B>Motion Frames:</B> " + str(motion_frames) + "<br>")
print ("<B>Straight Line:</B> " + str(straight_line) + "<br>")
print ("<B>Meteor Y/N:</B> " + str(meteor_yn) + "<br>")
print ("<B>Motion Events:</B> " + str(motion_events) + "<br>")
print ("<B>Consecutive Motion:</B> " + str(cons_motion) + "<br>")
print ("<B>Event Contours:</B> " + str(event_cnts) + "<br>")








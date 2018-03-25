#!/usr/bin/python3
import subprocess 
video_dir = "/mnt/ams2/"
print ("Content-type: text/html\n\n")

print ("<h2>Motion Events</h2>")

cmd = "find /mnt/ams2/SD | grep motion |grep mp4 "
print (cmd)
output = subprocess.check_output(cmd, shell=True).decode("utf-8")
files = output.split("\n")

for file in sorted(files):
   print (file)

#output = int(output.replace("\n", ""))

print ("<PRE>")
print(str(output) + "  <BR>")
print ("</PRE>")




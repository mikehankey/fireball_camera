#!/usr/bin/python3
import glob
import subprocess
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"


print ("Content-type: text/html\n\n")
form = cgi.FieldStorage()
file = form.getvalue('file')



el = file.split("/");
if len(el) != 5:
   print ("bad file" + str(len(el)) + "<BR>")
   exit()

if " " in file or ";" in file or "|" in file or ">" in file:
   print ("bad file space<BR>")
else:
   cmd = "rm " + file
   os.system(cmd)
   print ("{ \"data\": { \"status\": \"" + cmd + "\" } }" )



#!/usr/bin/python3
import glob
import sys
import subprocess
import os
import time

video_dir = "/media/ams/Samsung_T5/video"

def start_capture(cam_num):
   cmd = "/home/ams/bin/ffmpeg -i rtsp://192.168.176.7" + cam_num + "/av0_0 -c copy -map 0 -f segment -strftime 1 -segment_time 60 -segment_format mp4 \"" + "/media/ams/Samsung_T5/video/" + cam_num + "/capture-%Y-%m-%d_%H-%M-%S.mp4\" 2>&1 > /dev/null & "
   os.system(cmd)

def stop_capture(cam_num):
   #print ("Stopping capture for ", cam_num)
   cmd = "kill -9 `ps -aux | grep ffmpeg |grep -v grep| awk '{print $2}'`"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   print (output)

def purge(cam_num):
   cur_time = int(time.time())
   #cmd = "rm " + cam_num + "/*"
   #print (cmd)
   #os.system(cmd)

   for filename in (glob.glob(video_dir + '/' + cam_num + '/*.mp4')):
      st = os.stat(filename)
      mtime = st.st_mtime
      tdiff = cur_time - mtime
      tdiff = tdiff / 60 / 60 / 24
      if tdiff >= .8:
         cmd = "rm " + filename
         print(cmd)
         os.system(cmd)
         #file_list.append(filename)




try:
   cmd = sys.argv[1]
   cam_num = sys.argv[2]
except:
   do_all = 1


if (cmd == "stop"):
   stop_capture("1")
if (cmd == "start"):
   start_capture(cam_num)
if (cmd == "start_all"):
   start_capture("1")
   start_capture("2")
   start_capture("3")
   start_capture("4")
   start_capture("5")
   start_capture("6")

if (cmd == "purge"):
   purge(cam_num)

if (cmd == "purge_all"):
   purge("1")
   purge("2")
   purge("3")
   purge("4")
   purge("5")
   purge("6")



#ffmpeg -i rtsp://192.168.176.71/av0_1 -c copy -map 0 -f segment -segment_time 60 -segment_format mp4 "1/capture-1-%03d.mp4" &

import numpy as np
import requests
import cv2
import os
import time
import datetime
from collections import deque


def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
      #print key, value
    return(config)


config = read_config()
print ("Sensing Up.")
r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=25&paramstep=0&paramreserved=0&")

cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1&user=admin&password=admin")

cv2.setUseOptimized(True)
time_start = time.time()
time.sleep(2)
lock = open("/home/pi/fireball_camera/calibrate.txt", "w")

cap.set(3, 640)
cap.set(4, 480)
frames = deque(maxlen=200) 
frame_times = deque(maxlen=200) 
count = 0

print ("Collecting calibration video.")
while count < 91:
   _ , frame = cap.read()
   if _ is True:
      frame_time = time.time()
      frames.appendleft(frame)
      frame_times.appendleft(frame_time)

   if count == 90:
      print ("Saving video.")
      dql = len(frame_times) - 1
      time_diff = frame_times[1] - frame_times[dql]
      fps = 90 / time_diff
      format_time = datetime.datetime.fromtimestamp(int(frame_time)).strftime("%Y%m%d%H%M%S")
      outfile = "{}/{}.avi".format("/var/www/html/out/cal", format_time)
      writer = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*'MJPG'), fps, (frames[0].shape[1], frames[0].shape[0]), True)
      while frames:
         img = frames.pop()
         frame_time = frame_times.pop()
         format_time = datetime.datetime.fromtimestamp(int(frame_time)).strftime("%Y%m%d%H%M%S")
         dec_sec = datetime.datetime.fromtimestamp(int(frame_time)).strftime("%f")
         format_time = format_time + dec_sec
         writer.write(img)
      writer.release()
   count = count + 1

# sense camera down
r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=50&paramstep=0&paramreserved=0&")
exit()
print("Stack File")
cap.release()
time.sleep(2)
count = 0
print ("/var/www/html/out/cal/" + outfile)
cap = cv2.VideoCapture("/var/www/html/out/cal/" + outfile)
cv2.namedWindow('pepe')
time.sleep(2)
count = 0
image_acc = None
while count < 90:
   _ , frame = cap.read()
   print (count)
   if frame is None:
      #print ("eof!", outfile)
      continue

   #alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
   
   alpha = .23
   nice_frame = frame
   #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
   #frame = cv2.GaussianBlur(frame, (21, 21), 0)
   if image_acc is None:
      image_acc = np.empty(np.shape(frame))
   image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
   hello = cv2.accumulateWeighted(frame, image_acc, alpha)

   cv2.imshow('pepe', frame)  
   count = count + 1

os.system("rm /home/pi/fireball_camera/calibrate.txt")

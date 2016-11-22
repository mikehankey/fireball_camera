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
while True:
   _ , frame = cap.read()
   if _ is True:
      frame_time = time.time()
      frames.appendleft(frame)
      frame_times.appendleft(frame_time)

   count = count + 1
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
      exit()

os.system("rm /home/pi/fireball_camera/calibrate.txt")
r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=25&paramstep=0&paramreserved=0&")

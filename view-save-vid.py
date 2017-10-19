import cv2
import time
from collections import deque

video_file = "../fireball_videos/20171018054312-ward.avi";
outfile = "../fireball_videos/20171018054312-ward-8FPS.avi";
cap = cv2.VideoCapture(video_file)
fps = 5.645677027472006 

time.sleep(1)
frames = deque(maxlen=201)

count = 0
while True:
   _ , frame = cap.read()
   if frame is None:
      if count <= 1:
         print("Bad file.")
      else:
         print ("Done.", count)
         writer = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*'X264'), fps, (height, width), True)
         while frames:
            img = frames.pop()
            writer.write(img)
         writer.release()
         exit()
   else: 
      print (count);
      height = frame.shape[1]
      width = frame.shape[0]
      if count > 115 and count < 180:
         frames.appendleft(frame)
   count = count + 1

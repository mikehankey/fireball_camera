import cv2
import iproc
import time
import sys 
import numpy as np
from collections import deque

def compute_straight_line(x1,y1,x2,y2,x3,y3):
   if x2 - x1 != 0:
      a = (y2 - y1) / (x2 - x1)
   else:
      a = 0
   if x3 - x1 != 0:
      b = (y3 - y1) / (x3 - x1)
   else:
      b = 0
   straight_line = a - b
   if (straight_line < 1):
      straight = "Y"
   else:
      straight = "N"
   return(straight_line)


frame_count = 0
tstamp_prev = None
image_acc = None
last_frame = None
xs = []
ys = []
motion_frames = []
colors = []
cv2.namedWindow('pepe')
cv2.namedWindow('pepe2')

video_file = sys.argv[1]
cap = cv2.VideoCapture(video_file)

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
         total_motion = len(motion_frames)
         half_motion = int(total_motion/2) 
         avg_color = sum(colors) / float(len(colors))
         x1 = xs[1]
         y1 = xs[1]
         x2 = xs[half_motion]
         y2 = xs[half_motion]
         x3 = xs[total_motion-2]
         y3 = xs[total_motion-2]
         straight_line = compute_straight_line(x1,y1,x2,y2,x3,y3)
         if (straight_line < 1 and straight_line > 0) or avg_color > 190:
            meteor_yn = "Y"
         else:
            meteor_yn = "N"
         print ("Total Motion: ", total_motion)
         print ("Average color: ", avg_color)
         print ("Straight Line: ", straight_line)


         #writer = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*'X264'), fps, (height, width), True)
         #while frames:
         #   img = frames.pop()
         #   writer.write(img)
         #writer.release()
         exit()
   else: 
      nice_frame = frame
      if last_frame == None:
         last_frame = frame

      alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
      #frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      gray_frame = frame
      frame = cv2.GaussianBlur(frame, (21, 21), 0)
      if last_frame is None:
         last_frame = nice_frame
      if image_acc is None:
         image_acc = np.empty(np.shape(frame))
      image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
      #image_diff = cv2.absdiff(last_frame.astype(last_frame.dtype), frame,)
      hello = cv2.accumulateWeighted(frame, image_acc, alpha)
      _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
      thresh= cv2.dilate(threshold, None , iterations=2)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      data = str(frame_count) + "|"

      color = 0
      contours = len(cnts)
      x,y,w,h = 0,0,0,0

      if contours > 0:
          for (i,c) in enumerate(cnts):
             x,y,w,h = cv2.boundingRect(cnts[0])
             x2 = x + w
             y2 = y + h
             crop_frame = gray_frame[y:y2,x:x2]
             params = cv2.SimpleBlobDetector_Params()
             params.blobColor = 255
             params.minThreshold = 10
             params.maxThreshold = 255
             params.filterByArea = True
             params.minArea = 5
             params.filterByConvexity = True
             params.minConvexity = 0.1


             detector = cv2.SimpleBlobDetector_create(params)
             keypoints = detector.detect(crop_frame)
             
             print (keypoints)
             crop_frame_k = cv2.drawKeypoints(crop_frame, keypoints, np.array([]), (255,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
             cv2.imshow('pepe2', crop_frame_k)

             M = cv2.moments(cnts[0])
             #print (M)
             k = cv2.isContourConvex(cnts[0])
             #print(k)
             cv2.rectangle(nice_frame, (x,y), (x+w, y+h), (0,255,0),2)
             mx = x + w
             my = y + h
             cx = int(x + (w/2))
             cy = int(y + (h/2))
             color = gray_frame[cy,cx]
             xs.extend([x])
             ys.extend([y])
             if contours == 1:
                colors.extend([color])
             motion_frames.extend([frame_count])
             text = " x,y: " + str(x) + "," + str(y) + " Contours: " + str(contours) + " Convex: " + str(k) + " Color: " + str(color)
             cv2.putText(nice_frame, text,  (x,y), cv2.FONT_HERSHEY_SIMPLEX, .4, (255, 255, 255), 1)
             nice_frame = cv2.circle(nice_frame,(cx,cy), 3, (0,0,255), -1)
      #cv2.imshow('pepe', thresh)
      cv2.imshow('pepe', nice_frame)
      #cv2.imshow('pepe', image_diff)
      cv2.waitKey(int(5000 / 25))
      print (count, x,y, contours, color);
      height = frame.shape[1]
      width = frame.shape[0]
      #if count > 115 and count < 180:
      #   frames.appendleft(frame)
   count = count + 1
   last_frame = nice_frame



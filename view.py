from collections import deque
from PIL import Image, ImageChops
from queue import Queue
import multiprocessing
import datetime
import cv2
import numpy as np
import iproc 
import time
import sys
MORPH_KERNEL       = np.ones((10, 10), np.uint8)

def view(file):
    jpg = file
    jpg = jpg.replace(".avi", ".jpg");
    jpg = jpg.replace("out", "jpgs");

    cap = cv2.VideoCapture(file)
    final_cv_image = None
    time.sleep(2)

    tstamp_prev = None
    image_acc = None
    nice_image_acc = None
    final_image = None
    cur_image = None
    cv2.namedWindow('pepe')
    count = 0
    frames = deque(maxlen=256)

 
    while True:
        frame_file = jpg.replace(".jpg", "-" + str(count) + ".jpg");
        _ , frame = cap.read()
        cv2.imwrite(frame_file, frame)
        if frame is None:
           if count == 0:
               print ("bad file!")
               exit()
           print (jpg)
           #cv2.imwrite(jpg, final_cv_image)
           exit()

#        frames.appendleft(frame)

        alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)

        frame = cv2.resize(frame, (0,0), fx=0.8, fy=0.8)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
        if image_acc is None:
            image_acc = np.empty(np.shape(frame))
        image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
        hello = cv2.accumulateWeighted(frame, image_acc, alpha)
        _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
        thresh= cv2.dilate(threshold, None , iterations=2)
        (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) > 0:
            area = cv2.contourArea(cnts[0])
            print ("Area:", area)
            perim = cv2.arcLength(cnts[0], True)
            print ("Perim:", perim)

            x,y,w,h = cv2.boundingRect(cnts[0])
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

            poly = cv2.approxPolyDP(cnts[0], 0.02*perim, True)

            #print ("Poly: ", poly)
            print ("Convex?: ", cv2.isContourConvex(cnts[0]))





        #nice_avg = cv2.convertScaleAbs(nice_image_acc)

        #print (cnts)


        if cur_image is None:
            cur_image = Image.fromarray(frame)

            #temp = cv2.convertScaleAbs(nice_image_acc)
            #nice_image_acc_pil = Image.fromarray(temp)
            #cur_image = ImageChops.lighter(cur_image, nice_image_acc_pil)

        #final_cv_image = np.array(cur_image)
        #cv2.imshow('pepe', final_cv_image)
        if count % 2 == 0:
            cv2.imshow('pepe', frame)
        count = count + 1
        #print (count)
        cv2.waitKey(1)

file = sys.argv[1]
view(file)

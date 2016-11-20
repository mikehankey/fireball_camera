import collections
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
import os
MORPH_KERNEL       = np.ones((10, 10), np.uint8)

def analyze(file):
    elapsed_frames = 0
    cons_motion = 0
    straight_line = 100
    straight = 'N'
    motion = 0
    motion_off = 0
    frame_data = {}
    data_file = file.replace(".avi", ".txt");
    summary_file = data_file.replace(".txt", "-summary.txt")
    fp = open(data_file, "r")
    sfp = open(summary_file, "w")
    event_start_frame = 0
    event_end_frame = 0
    sum_color = 0
    for line in fp:
       (frame,countours,area,perimeter,convex,x,y,w,h,color,n) = line.split("|")
       if frame != 'frame':
          if countours != "":
             motion = motion + 1
             motion_off = 0
          if motion == 1 and countours == "":
             motion = 0
          if motion == 5 and event_start_frame == 0:
             event_start_frame = int(frame) 
          if motion >= 1 and countours == "":
             motion_off = motion_off + 1
          if motion > 5 and motion_off > 5 and event_end_frame == 0:
             cons_motion = motion
             event_end_frame = int(frame) - 5 
          out = str(frame)+","+str(motion)+","+str(x)+","+str(y)+","+str(countours)+",\n"
          sfp.write(out)
          if (event_start_frame != 0 and event_end_frame == 0 and color != ""):
             #print ("COLOR:", color)
             sum_color = sum_color + int(color)
          frame_data.update({int(frame) : {'x': x, 'y': y}})
    out = "Event Start Frame : " + str(event_start_frame) + "\n"
    sfp.write(out)
    out = "Event End Frame : " + str(event_end_frame) + "\n"
    sfp.write(out)
    key_frame1 = int(event_start_frame)
    key_frame2 = int(event_start_frame + ((int(event_end_frame - event_start_frame) / 2)))
    key_frame3 = int(event_end_frame - 3)
    ofr = collections.OrderedDict(sorted(frame_data.items()))

    out = "KEY FRAMES: " + str(key_frame1) + "," + str(key_frame2) + "," + str(key_frame3)
    sfp.write(out)
    elapsed_frames = key_frame3 - key_frame1
    if elapsed_frames > 0:
       avg_center_pixel = sum_color / elapsed_frames
    else:
       avg_center_pixel = 0
    out = "SUM COLOR/Frames: " + str(sum_color) + "/" + str(elapsed_frames)
    sfp.write(out)
    if cons_motion > 10 and event_end_frame > 0 and 'x' in frame_data[key_frame3] and 'x' in frame_data[key_frame2] and 'x' in frame_data[key_frame1]:
       if ( frame_data[key_frame1]['x'] != '' and frame_data[key_frame2]['x'] != '' and frame_data[key_frame3]['x'] != '' ):
          x1 = int(frame_data[key_frame1]['x'])
          y1 = int(frame_data[key_frame1]['y'])
          #print("X2: ", frame_data[key_frame2]['x'])
          x2 = int(frame_data[key_frame2]['x'])
          y2 = int(frame_data[key_frame2]['y'])
          x3 = int(frame_data[key_frame3]['x'])
          y3 = int(frame_data[key_frame3]['y'])

          a = (y2 - y1) / (x2 - x1)
          b = (y3 - y1) / (x3 - x1)
          straight_line = a - b
          if (straight_line < 1):
             straight = "Y" 
    else: 
       out = "Not enough consecutive motion."
       sfp.write(out)
       
    meteor = "N"
    if (straight_line < 1 and avg_center_pixel > 500):
       meteor = "Y"
    sfp.write("Elapsed Frames:\t" + str(elapsed_frames)+ "\n")
    sfp.write("Straight Line:\t" + str(straight) + "," + str(straight_line)+"\n")
    sfp.write("Average Center Pixel Color:\t" + str(avg_center_pixel) + "\n")
    sfp.write("Likely Meteor:\t"+ str(meteor)+"\n")
    if meteor == "N":
       false_file= file.replace("out/", "out/false/")
       false_data_file= data_file.replace("out/", "out/false/")
       false_summary_file= summary_file.replace("out/", "out/false/")
       cmd = "mv " + file + " " + false_file 
       os.system(cmd)
       cmd = "mv " + data_file + " " + false_data_file
       os.system(cmd)
       cmd = "mv " + summary_file + " " + false_summary_file
       os.system(cmd)
  
def view(file):
    jpg = file
    data_file = file
    jpg = jpg.replace(".avi", ".jpg");
    jpg = jpg.replace("out", "jpgs");
    data_file = data_file.replace(".avi", ".txt");

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

    fp = open(data_file, "w")
    fp.write("frame|countours|area|perimeter|convex|x|y|w|h|color|\n")
    mid_pix_total = 0
    while True:
        frame_file = jpg.replace(".jpg", "-" + str(count) + ".jpg");
        _ , frame = cap.read()
        #cv2.imwrite(frame_file, frame)
        if frame is None:
           if count == 0:
               print ("bad file!")
               return()
           #print (jpg)
           #cv2.imwrite(jpg, final_cv_image)
           return()
           #exit()

#        frames.appendleft(frame)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
        #print ("ALPHA: ", alpha)
        nice_frame = frame
        #frame = cv2.resize(frame, (0,0), fx=0.8, fy=0.8)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
        if image_acc is None:
            image_acc = np.empty(np.shape(frame))
        image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
        hello = cv2.accumulateWeighted(frame, image_acc, alpha)
        _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
        thresh= cv2.dilate(threshold, None , iterations=2)
        (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        data = str(count) + "|" 
        if len(cnts) > 0:
            area = cv2.contourArea(cnts[0])
            perim = cv2.arcLength(cnts[0], True)
            #print ("Perim:", perim)

            x,y,w,h = cv2.boundingRect(cnts[0])

            #ellipse = cv2.fitEllipse(cnts[0])
            #print ("Ellipse:", len(ellipse), ellipse)
            #if len(ellipse) == 5:
            #   cv2.ellipse(frame,ellipse,(0,255,0),2)

            # crop out
            x2 = x+w
            y2 = y+h
            mx = x + (w/2)
            my = y + (h/2)
            #print ("XY:", x,x2,y,y2)
            middle_pixel = nice_frame[my,mx]
            middle_sum = np.sum(middle_pixel)
            #print("MID PIX:", middle_pixel, middle_sum)
            mid_pix_total = mid_pix_total + middle_sum
            crop_frame = nice_frame[y:y2,x:x2]
            avg_color_per_row = np.average(crop_frame, axis=0)
            avg_color = np.average(avg_color_per_row, axis=0)
            #print ("AVG COLOR: " , avg_color, np.sum(avg_color))
            tjpg = jpg
            tjpg = tjpg.replace(".jpg", "-" + str(count) + ".jpg")
           # print ("TJPG", tjpg)
            cv2.imwrite(tjpg, crop_frame)


            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,255),1)

            poly = cv2.approxPolyDP(cnts[0], 0.02*perim, True)

            #print ("Poly: ", poly)
            #print ("Convex?: ", cv2.isContourConvex(cnts[0]))
            convex = cv2.isContourConvex(cnts[0])
            #data = "frame|countours|area|perimeter|poly|convex|x|y|w|h|color|\n" 
            data = data + str(len(cnts)) + "|" + str(area) + "|" + str(perim) + "|"
            #data = data + str(poly) + "|"
            data = data + str(convex) + "|"
            data = data + str(x) + "|"
            data = data + str(y) + "|"
            data = data + str(w) + "|"
            data = data + str(h) + "|"
            data = data + str(middle_sum) + "|"
        else:
            data = data + "|||||||||"
        fp.write(data + "\n")
     





        #nice_avg = cv2.convertScaleAbs(nice_image_acc)

        #print (cnts)


        if cur_image is None:
            cur_image = Image.fromarray(frame)

            #temp = cv2.convertScaleAbs(nice_image_acc)
            #nice_image_acc_pil = Image.fromarray(temp)
            #cur_image = ImageChops.lighter(cur_image, nice_image_acc_pil)

        #final_cv_image = np.array(cur_image)
        #cv2.imshow('pepe', final_cv_image)
        if count % 1 == 0:
            cv2.imshow('pepe', frame)
        count = count + 1
        #print (count)
        cv2.waitKey(1)

file = sys.argv[1]

#view("/var/www/html/out/" + file)
print ("Analyze it...")
analyze("/var/www/html/out/" + file)



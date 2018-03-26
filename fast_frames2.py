#!/usr/bin/python3 

from astride import Streak
from astropy.io import fits
from PIL import Image, ImageChops
import time
import multiprocessing
import cv2
import sys
import numpy as np

#queue_from_cam = multiprocessing.Queue()
stack_queue = multiprocessing.Queue()
#queue_for_brightness = multiprocessing.Queue()


def brightness_loop(queue_for_brightness, file):
   cv2.namedWindow('pepe')
   print ("STACK LOOP!")
   start_time = int(time.time())
   cc = 0
   skip = 0
   max_pixels = []
   image_acc = None
   mask_regions = []
   while True:
      if queue_for_brightness.empty():   
         skip = skip + 1
         if skip > 50000 or cc > 1499:
            print ("brightness process done")
            break
      else:
         frame = queue_for_brightness.get()
         if cc == 0:
            _, bright_regions = cv2.threshold(frame, 50, 255, cv2.THRESH_BINARY)
            bright_regions = cv2.dilate(bright_regions, None , iterations=2)

            (_, cnts, xx) = cv2.findContours(bright_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(cnts) > 0:
               for (i,c) in enumerate(cnts):
                  x,y,w,h = cv2.boundingRect(cnts[i])
                  if w > 5 and h > 5:
                     x = x - 20 
                     y = y - 20
                     w = w + 20
                     h = h + 20  
                     if x < 0: 
                        x = 0
                     if y < 0: 
                        y = 0
                     if x+ w >= 640: 
                        w = 640 
                     if y+ h >= 480: 
                        h = 0
                     mask_regions.append ((x,y,w,h)) 
                     print ("MASK: ", x,y,w,h)
                     frame[y:y+h,x:x+w] = [0]
         for x,y,w,h in mask_regions:          
            frame[y:y+h,x:x+w] = [0]
            #cv2.rectangle(frame, (x,y), (x+w, y+h), (255),2)

         if cc % 1 == 0:

            # mask out bright areasA
            
            if image_acc is None:
               image_acc = np.empty(np.shape(frame))

            #acc_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
            hello = cv2.accumulateWeighted(frame.copy(), image_acc, .5)


            # determine brightness 

            if cc > 0:
               image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)

               _, threshold = cv2.threshold(image_diff, 10, 255, cv2.THRESH_BINARY)
               (_, cnts, xx) = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
               real_cnts = []
               if len(cnts) > 0:
                  for (i,c) in enumerate(cnts):
                     x,y,w,h = cv2.boundingRect(cnts[i])
                     cv2.rectangle(frame, (x,y), (x+w, y+h), (255,255,255),2)
                     if w > 3 and h > 3 and (x > 1 and y > 1):
                        real_cnts.append([x,y,w,h])



               #if cc % 5 == 0:
               max_px = np.sum(threshold) / 255
               max_pixels.append((cc,max_px))
               #text = "frame " + str(cc) + " CNTS: " + str(len(real_cnts))
               #cv2.putText(threshold, text,  (20,20), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)

               #cv2.imshow('pepe', frame)
               #cv2.waitKey(10000)

            if cc % 100 == 0:
               print ('brightness eval ', cc)
         cc = cc + 1
         skip = 0
   end_time = int(time.time())
   elapsed = end_time - start_time
   print ("PROCESSED BRIGHTNESS IN: ", elapsed)
   np_max_pixels = np.array(max_pixels)
   jk,br_avg = np_max_pixels.mean(axis=0)
   for fc,br in max_pixels:
      factor = br / br_avg
      if factor >= 1.1:
         print (fc,br_avg, br, factor, "+++++")
      else:
         print (fc,br_avg, br, factor)



def stack_loop(stack_queue, file):
   print ("STACK LOOP!")
   start_time = int(time.time())
   cc = 0
   skip = 0
   stack_file = file.replace(".mp4", "-stacked.jpg")
   stacked_image = None
   while True:
      if stack_queue.empty():   
         skip = skip + 1
         if skip > 2000 or cc > 1499:
            print ("stack process done")
            break
      else:
         frame = stack_queue.get()
         if frame is not None:
            if cc % 1 == 0:
               frame_pil = Image.fromarray(frame)
               if stacked_image is None:
                  stacked_image = frame_pil
               else: 
                  stacked_image=ImageChops.lighter(stacked_image,frame_pil)

               # stack image here!
               if cc % 100 == 0:
                  print ('stack image', cc)
            cc = cc + 1
            skip = 0
   end_time = int(time.time())
   elapsed = end_time - start_time
   print ("PROCESSED STACK IN: ", elapsed)
   if stacked_image is not None:   
      stacked_image.save(stack_file, "JPEG")
   else: 
      print("Failed.")

   #np_stacked_image = np.asarray(stacked_image) 
   #np_stacked_image = cv2.cvtColor(np_stacked_image, cv2.COLOR_BGR2GRAY)
   #fits.writeto('stack.fits', np_stacked_image, overwrite=True)
   #streak = Streak('stack.fits')
   #streak.detect()
   #streak.plot_figures()
   #stacked_image.show()

def gray_loop(queue_from_cam, queue_for_brightness, file):
   print ("GRAY LOOP!")
   start_time = int(time.time())
   cc = 0
   skip = 0
   while True:
      if queue_from_cam.empty():   
         skip = skip + 1
         if skip > 10000 or cc > 1499:
            print ("gray process done")
            break
      else:
         frame = queue_from_cam.get()
         if cc % 1 == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #queue_from_gray.put(frame)

            #frame[400:480, 0:640] = [0]
            frame = cv2.GaussianBlur(frame, (21, 21), 0)
            queue_for_brightness.put(frame)
            if cc % 100 == 0:
               print ('converted frame to gray', cc)
         cc = cc + 1
         skip = 0
   end_time = int(time.time())
   elapsed = end_time - start_time
   print ("PROCESSED GRAY IN: ", elapsed)


def cam_loop(stack_queue, file):
    #frames = [] 
    print ('initializing cam')
    go = 1
    fc = 0
    fail = 0
    cap = cv2.VideoCapture(file)
    while go == 1:
       hello, frame = cap.read()
       if frame is None:
          #print ("Frame is NONE")
          fail = fail + 1
          print ("Fail: ", fail)
          if fail > 10 : 
             #stack_queue.put(frame)
             go = 0
             break
          #else:
          #   go = 0
          #   break
       else:
          #frames.append(frame)
          if fc % 2 == 0:   
             #print ('grabbed frame', fc)
             #queue_from_cam.put(frame)
             stack_queue.put(frame)
          fc = fc + 1
    print ("PROCESSED FILE CAPTURE ", file )
    cap.release()

file = sys.argv[1]

cam_process = multiprocessing.Process(target=cam_loop,args=(stack_queue, file))
#gray_process = multiprocessing.Process(target=gray_loop,args=(queue_from_cam, queue_for_brightness, file))
stack_process = multiprocessing.Process(target=stack_loop,args=(stack_queue, file))
#brightness_process = multiprocessing.Process(target=brightness_loop,args=(queue_for_brightness, file))
cam_process.start()
#gray_process.start()
stack_process.start()
#time.sleep(10)
#stack_process.terminate()

#brightness_process.start()



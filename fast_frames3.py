#!/usr/bin/python3 

from astride import Streak
from astropy.io import fits
from PIL import Image, ImageChops
import time
import multiprocessing
import cv2
import sys
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#queue_from_cam = multiprocessing.Queue()
stack_queue = multiprocessing.Queue()
#queue_for_brightness = multiprocessing.Queue()


def stack_loop(stack_queue, file):
   start_time = int(time.time())
   cc = 0
   skip = 0
   stack_file = file.replace(".mp4", "-stacked.jpg")
   stacked_image = None
   frame = None
   while frame != 'STOP':
      frame = stack_queue.get()
      if frame is not None and frame != 'STOP':
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

   end_time = int(time.time())
   elapsed = end_time - start_time
   print ("PROCESSED STACK IN: ", elapsed)
   if stacked_image is not None:   
      print("saving", stack_file)
      stacked_image.save(stack_file, "JPEG")
   else: 
      print("Failed.")
      failed_file = stack_file.replace("stacked.jpg", "fail.txt")
      fp = open(failed_file, "w")
      fp.close()

   #np_stacked_image = np.asarray(stacked_image) 
   #np_stacked_image = cv2.cvtColor(np_stacked_image, cv2.COLOR_BGR2GRAY)
   #fits.writeto('stack.fits', np_stacked_image, overwrite=True)
   #streak = Streak('stack.fits')
   #streak.detect()
   #streak.plot_figures()
   #stacked_image.show()

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
          #print ("Fail: ", fail)
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
    stack_queue.put("STOP")
    print ("VIDEO FILE", file )
    print ("FRAMES:", fc)
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



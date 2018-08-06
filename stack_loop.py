import cv2
import numpy as np
from PIL import Image, ImageChops
import time
import os
from pathlib import Path
#from cpython cimport array

def finish_up(file):
   frame_data_final = file.replace(".mp4", "-frame_data.txt")
   stack_file = file.replace(".mp4", "-stacked.jpg")
   stacked_image = None
   for i in range(1,6):
      frame_data_part = file.replace(".mp4", "-frame_data" + str(i) + ".txt")
      part_stack = file.replace(".mp4", "-stacked" + str(i) + ".jpg")

      fd_exists = Path(frame_data_part)
      if (fd_exists.is_file() == True):

         if i == 1:
            cmd = "cat " + frame_data_part + "> " + frame_data_final
         else:
            cmd = "cat " + frame_data_part + ">> " + frame_data_final
         os.system(cmd)
         cmd = "rm " + frame_data_part
         os.system(cmd)

      file_exists = Path(part_stack)
      if (file_exists.is_file() == True):
         st_img = cv2.imread(part_stack,1)

         if st_img is not None:
            frame_pil = Image.fromarray(st_img)
            if stacked_image is None:
               stacked_image = frame_pil
            else:
               stacked_image=ImageChops.lighter(stacked_image,frame_pil)

   if stacked_image is not None:
      stacked_image.save(stack_file, "JPEG")


def stack_loop(stack_queue, file, thread_num, start_time):
   cc = (thread_num - 1 ) * 300
   skip = 0

   stack_file = file.replace(".mp4", "-stacked" + str(thread_num) + ".jpg")
   motion_file = file.replace(".mp4", "-motion" + str(thread_num) + ".txt")
   rpt_file = file.replace(".mp4", "-frame_data" + str(thread_num) + ".txt")
   rpt = open(rpt_file, "w")

   stacked_image = None
   frame = None
   last_frame = None
   image_acc = None
   mx_roll = 0
   mx_av = 0
   cons_motion = 1
   motion_on = 0
   motion_off = 0
   motion_events = []
   motion_frames = []
   stop_motion = 0
   motion_detect_on = 0 
   while frame != 'STOP':
      frame = stack_queue.get()

      if frame is not None and frame != 'STOP' and frame != 'SKIP':

         # motion dection here....
         if motion_detect_on == 1:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame[440:480, 0:640] = [0]
            if image_acc is None:
               image_acc = np.empty(np.shape(gray_frame))
            hello = cv2.accumulateWeighted(gray_frame.copy(), image_acc, .5)
            image_diff = cv2.absdiff(image_acc.astype(gray_frame.dtype), gray_frame,)
            av = np.average(image_diff)
            mx = np.max(image_diff)
            mx_roll = mx_roll + mx
            if cc > 0:
               mx_avg = mx_roll / ((cc + 1) - ((thread_num - 1 ) * 300))
               mx_avg = round(mx_avg, 2)
            else:
               mx_avg = mx_roll
            av = round(av, 2)
            if mx > (mx_avg * 2):
               thresh = cv2.adaptiveThreshold(image_diff,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,-20)
               (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            else:
               cnts = []
            rpt.write(str(cc) + "\t" + str(av) + "\t" + str(mx_roll) + "\t" + str(mx_avg) + "\t" + str(mx) + "\t" + str(len(cnts)) + "\n")
            if len(cnts) > 0:
               if motion_on == 1:
                  cons_motion = cons_motion + 1
                  motion_frames.append(cc)
               else:
                  # event started
                  motion_on = 1
                  stop_motion = 0
                  cons_motion = cons_motion + 1
                  motion_frames.append(cc)
            else:
               motion_on = 0
               stop_motion = stop_motion + 1
            if cons_motion >= 1 and motion_on == 0:
               stop_motion = stop_motion + 1
            if cons_motion >= 1 and stop_motion >= 3:
               # end of event
               if len(motion_frames) > 1:
                  motion_events.append(motion_frames)
               motion_frames = []
               stop_motion = 0
               cons_motion = 0
               motion_on = 0

         frame_pil = Image.fromarray(frame)
         if stacked_image is None:
            stacked_image = frame_pil
         else:
            #if av < 7:
            stacked_image=ImageChops.lighter(stacked_image,frame_pil)

      else:
         rpt.write(str(cc) + "\t" + "skip" + "\t" + "skip" + "\t" + "skip" + "\t" + "skip" + "\t" + "skip" + "\n")
      cc = cc + 1
   rpt.close()
   motion_detected = 0
   for motion_event in motion_events:
      if len(motion_event) >= 3:
         motion_detected = 1
   if motion_detected == 1:
      mfp = open(motion_file, "w")
      mfp.write(str(motion_events))
      #print ("Motion detected", motion_events)

   if stacked_image is not None:
      stacked_image.save(stack_file, "JPEG")
   else:
      print("Failed.")
      failed_file = stack_file.replace("stacked.jpg", "fail.txt")
      fp = open(failed_file, "w")
      fp.close()

def cam_loop(stack_queue, stack_queue2, stack_queue3, stack_queue4, stack_queue5, file):
    #frames = []
    #print ('initializing cam')
    go = 1
    fc = 0
    fail = 0
    cap = cv2.VideoCapture(file)
    while go == 1:
       hello, frame = cap.read()
       if frame is None:
          fail = fail + 1
          if fail > 10 :
             go = 0
             break
       else:
          if True:
             if fc < 300:
                if fc % 3 != 0:
                   stack_queue.put(frame)
                else:
                   stack_queue.put("SKIP")
             elif 300 <= fc < 600:
                if fc % 3 != 0:
                   stack_queue2.put(frame)
                else:
                   stack_queue2.put("SKIP")
             elif 600 <= fc < 900 :
                if fc % 3 != 0:
                   stack_queue3.put(frame)
                else:
                   stack_queue3.put("SKIP")
             elif 900 <= fc < 1200:
                if fc % 3 != 0:
                   stack_queue4.put(frame)
                else:
                   stack_queue4.put("SKIP")
             else:
                if fc % 3 != 0:
                   stack_queue5.put(frame)
                else:
                   stack_queue5.put("SKIP")
          fc = fc + 1
    stack_queue.put("STOP")
    stack_queue2.put("STOP")
    stack_queue3.put("STOP")
    stack_queue4.put("STOP")
    stack_queue5.put("STOP")
    cap.release()
    print ("FRAMES:", fc)


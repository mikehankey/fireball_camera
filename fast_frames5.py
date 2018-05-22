#!/usr/bin/python3 

import os
#import pyximport; pyximport.install()
import stack_loop
from pathlib import Path
from PIL import Image, ImageChops
import time
import multiprocessing
from multiprocessing import Process
import cv2
import sys
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

stack_queue = multiprocessing.Queue()
stack_queue2 = multiprocessing.Queue()
stack_queue3 = multiprocessing.Queue()
stack_queue4 = multiprocessing.Queue()
stack_queue5 = multiprocessing.Queue()



file = sys.argv[1]
start_time = int(time.time())

cam_process = multiprocessing.Process(target=stack_loop.cam_loop,args=(stack_queue, stack_queue2, stack_queue3, stack_queue4, stack_queue5, file))
stack_process = multiprocessing.Process(target=stack_loop.stack_loop,args=(stack_queue, file, 1, start_time))
stack_process2 = multiprocessing.Process(target=stack_loop.stack_loop,args=(stack_queue2, file, 2, start_time))
stack_process3 = multiprocessing.Process(target=stack_loop.stack_loop,args=(stack_queue3, file, 3, start_time))
stack_process4 = multiprocessing.Process(target=stack_loop.stack_loop,args=(stack_queue4, file, 4, start_time))
stack_process5 = multiprocessing.Process(target=stack_loop.stack_loop,args=(stack_queue5, file, 5, start_time))

cam_process.start()
stack_process.start()
stack_process2.start()
stack_process3.start()
stack_process4.start()
stack_process5.start()

procs = (stack_process, stack_process2, stack_process3, stack_process4, stack_process5)

done = 0
while done == 0:
   procs_alive = 0
   for proc in procs :
      proc.join(timeout=0)
      if proc.is_alive():
         time.sleep(.01)
         procs_alive = 1
   if procs_alive == 0:
      stack_loop.finish_up(file)
      done = 1

end_time = int(time.time())
elapsed = end_time - start_time
print ("PROCESSED FILE IN: ", elapsed)
print ("DONE: ", done)


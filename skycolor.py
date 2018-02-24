# import the necessary packages
import numpy as np
import cv2
import sys 
from amscommon import read_config

 

def get_cap(config):
   cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1")

   _ , frame = cap.read()
   cap.release()
   return(frame)


def is_it_clear(cam_num):
   # load the image
   config = read_config("conf/config-" + str(cam_num) + ".txt")
   #image = get_cap(config)
   image = cv2.imread("ffvids/1/time_lapse/capture-2018-02-20_18-07-10-stack.jpg")

   avg_color_per_row = np.average(image,axis=0)
   r,g,b = np.average(avg_color_per_row,axis=0)
   if (100 < r < 145) and (100 < g < 145) and (100 < b < 145) :
      print (str(cam_num) + " Looks clear :)")
      print(r,g,b)
   else:
      print (str(cam_num) + " Looks cloudy :(")
      print(r,g,b)

is_it_clear(1)
#is_it_clear(2)
#is_it_clear(3)
#is_it_clear(4)
#is_it_clear(5)
#is_it_clear(6)

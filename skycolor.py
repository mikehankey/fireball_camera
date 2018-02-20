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



# load the image
config = read_config("conf/config-1.txt")
image = get_cap(config)

avg_color_per_row = np.average(image,axis=0)
r,g,b = np.average(avg_color_per_row,axis=0)
print(r,g,b)
if (100 < r < 145) and (100 < g < 145) and (100 < b < 145) :
   print ("Looks clear :)")
else:
   print ("Looks cloudy :(")

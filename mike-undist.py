#!/usr/bin/python3

import numpy as np
import cv2
import sys
import math

#input:
#    strength as floating point >= 0.  0 = no change, high numbers equal stronger correction.
#    zoom as floating point >= 1.  (1 = no change in zoom)

#algorithm:



def undistort(file):
   img_cv = cv2.imread(file,1)
   h = img_cv.shape[0] 
   w = img_cv.shape[1]
   base_file = file.replace(".jpg", "-base.jpg")
   print("1st IMG ", img_cv.shape)

   base_size = h+200,w+200,3
   base = np.zeros(base_size,dtype=np.uint8) 
   base[100:h+100,100:w+100]=img_cv
   cv2.imwrite(base_file, base) 

   # plate img
   plate_file = file.replace(".jpg", "-distplot.png")
   plate_img_cv = cv2.imread(plate_file,1)
   plate_base = np.zeros(base_size,dtype=np.uint8) 
   plate_base[100:h+100,100:w+100]=plate_img_cv

   
   print("Plate Img Size", plate_img_cv.shape)
   print("Plate Base Size", plate_base.shape)

   img_cv = cv2.imread(base_file,1)
   h = img_cv.shape[0] 
   w = img_cv.shape[1]

   print("2nd IMG ", img_cv.shape)


   img_cv_new = np.zeros((h,w,3), np.uint8)
   out_file = file.replace(".jpg", "-und.jpg")
   half_w = w / 2
   half_h = h / 2
   half_w = half_w + 120
   half_h_ = half_h 
   strength = 1.8 
   zoom = 1
   correctionRadius = math.sqrt(w ** 2 + h ** 2) / strength

   for x in range(0,w-1):
      #print (w-1,x)
      for y in range(0,h-1):
         #print (h-1,y)
         newX = x - half_w
         newY = y - half_h

         distance = math.sqrt(newX ** 2 + newY ** 2)
         r = distance / correctionRadius
        
         if r == 0: 
            theta = 1
         else:
            theta = math.atan(r) / r

         sourceX = half_w + theta * newX * zoom
         sourceY = half_h + theta * newY * zoom

         sourceX = int(float(sourceX))
         sourceY = int(float(sourceY))

         #set color of pixel (x, y) to color of source image pixel at (sourceX, sourceY)
         newX = int(float(newX))
         newY = int(float(newY))
         if sourceY > h-1: 
            sourceY = h-1
         if sourceX > w-1: 
            sourceX = w-1 
         if newX % 1000 == 0:
            print ("NEW X,Y", x,y)
            print ("SOURCEX,Y", sourceX,sourceY)
         #print ("NEWX,Y", newX,newY)
         #print ("IMG1: ", img_cv[newY,newX])
         #print ("IMG2: ", img_cv_new[sourceX,sourceY])
         #img_cv_new[x,y] = img_cv[sourceX,sourceY]
         img_cv_new[y,x] = img_cv[sourceY,sourceX]
   print ("SHAPE1: ", img_cv_new.shape)
   print ("SHAPE2: ", plate_base.shape)
   blend = cv2.addWeighted(img_cv_new, .7, plate_base, .3,0)
   #cv2.imwrite(out_file, blend) 
   cv2.imwrite(out_file, img_cv_new) 

file = sys.argv[1]
undistort(file)

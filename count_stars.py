#!/usr/bin/python3
import cv2
import numpy as np
import sys
import os
import time 

jpg_file = sys.argv[1]

image = cv2.imread(jpg_file)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

limit_low = 60 
limit_up =  245
last_x = 0
last_y = 0
stars_found = 0
stars = []
data = None

for y in range(gray.shape[0] - 100):
   for x in range(gray.shape[1]):
      pixel = gray.item(y,x)
      if pixel > limit_low and pixel < limit_up: 
         x1 = x - 4 
         x2 = x + 5 
         y1 = y - 4 
         y2 = y + 5 
         x3 = x - 1 
         x4 = x + 1  
         y3 = y - 1 
         y4 = y + 1 
         crop_frame = gray[y1:y2,x1:x2]
         small_crop_frame = gray[y3:y4,x3:x4]

         avg_pix = np.average(crop_frame)
         avg_pix_s = np.average(small_crop_frame)
         diff = avg_pix_s - avg_pix

         x_y_diff = abs((last_x + last_y) - (x + y))
         if crop_frame.shape[0] > 0 and crop_frame.shape[1] > 0 and diff > 20 and (x_y_diff > 4):
            #print ("X,Y,AVG,SAVG,DIFF:", x,y,pixel,avg_pix, avg_pix_s, diff)


            o,p = np.unravel_index(crop_frame.argmax(), crop_frame.shape)
            off_x = p -4
            off_y = o -4 
            cor_x = x + off_x
            cor_y = y + off_y
            cor_val = gray[cor_y,cor_x] 
            x1 = cor_x - 4 
            x2 = cor_x + 5 
            y1 = cor_y - 4 
            y2 = cor_y + 5 
            x3 = cor_x - 1 
            x4 = cor_x + 1  
            y3 = cor_y - 1 
            y4 = cor_y + 1 

            new_crop_frame = gray[y1:y2,x1:x2]
            new_crop_frame_sm = gray[y3:y4,x3:x4]

            avg_pix = np.average(new_crop_frame)
            avg_pix_s = np.average(new_crop_frame_sm)
            
            last_x = x
            last_y = y
            pix_dif = avg_pix_s - avg_pix;
            stars.append((cor_x,cor_y,avg_pix,avg_pix_s,pix_dif)) 
            stars_found = stars_found + 1
      else:
         pass

dtype = [('x', int), ('y', int), ('avg_pix', float), ('avg_pix_s', float), ('pix_dif', float)]
star_arry = np.array(stars, dtype=dtype)
np.sort(star_arry, order='pix_dif')

#fp = open(star_data_file, "w")
#fp.write("x,y\n")
#print ("Stars Found: ", stars_found)
for star_x, star_y, pix_val, pix_val_sm,pix_dif in np.sort(star_arry,order='pix_dif')[::-1]:
      #data = str(star_x) + "," + str(star_y) + "\n"
      #print (star_x, star_y)
      #fp.write(data)
      cv2.circle(gray, (star_x, star_y), 10, (255,0,0), 1, 1)

#fp.close() 
time.sleep(1)

#cv2.imshow("Image", gray)
#cv2.waitKey(0)
print ("Total Stars Found: ", stars_found)

#cv2.imwrite(star_file, gray)



#xyfits = star_data_file.replace(".txt", ".fits")
#cmd = "/usr/bin/python /usr/local/astrometry/bin/text2fits.py -f \"ff\" -s \",\" " + star_data_file + " " + xyfits 
#print (cmd)
#os.system(cmd)

#cmd = "/usr/local/astrometry/bin/solve-field " + jpg_file + " --overwrite --width=640 --height=360 --width=640 --scale-low 50 --scale-high 95"
#cmd = "/usr/local/astrometry/bin/solve-field " + xyfits + " --overwrite --width=640 --height=360 --width=640 --scale-low 50 --scale-high 95"
#print (cmd)
#os.system(cmd)

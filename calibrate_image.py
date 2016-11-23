import cv2
import numpy as np

jpg_file = "20161123011608.jpg"
star_file = "20161123011608-stars.jpg"
image = cv2.imread(jpg_file)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#gray = cv2.GaussianBlur(gray, (1,1), 1)
#gray = cv2.medianBlur(gray, 1)
#cv2.imshow("Image", gray)
#cv2.waitKey(0)
limit_low = 80 
limit_up =  255
last_x = 0
last_y = 0
stars_found = 0
stars = []
for y in range(gray.shape[0] - 60):
   for x in range(gray.shape[1]):
      pixel = gray.item(y,x)
      if pixel > limit_low and pixel < limit_up: 
         x1 = x - 5 
         x2 = x + 5 
         y1 = y - 5 
         y2 = y + 5 
         x3 = x - 1 
         x4 = x + 1  
         y3 = y - 1 
         y4 = y + 1 
         crop_frame = gray[y1:y2,x1:x2]
         small_crop_frame = gray[y3:y4,x3:x4]
         avg_pix = np.average(crop_frame)
         avg_pix_s = np.average(small_crop_frame)
         print (x, y)
         print ("AVG,SAVG,DIFF:", avg_pix, avg_pix_s)
         #print ("SAVG:", avg_pix_s)
         diff = avg_pix_s - avg_pix
        

         x_y_diff = abs((last_x + last_y) - (x + y))
         print ("XYDIFF: ", x_y_diff)
         if crop_frame.shape[0] > 0 and crop_frame.shape[1] > 0 and diff > 20 and (x_y_diff > 8):
            
            #cv2.imshow("Image", crop_frame)
            #cv2.waitKey(0)
            last_x = x
            last_y = y
            #add pixel here
            stars.append((x,y)) 
            stars_found = stars_found + 1
      else:
         pass
 
print ("Stars Found: ", stars_found)
for star_x, star_y in stars:
   print (star_x, star_y)
   cv2.circle(gray, (star_x, star_y), 5, (255,0,0), 1, 1)

cv2.imshow("Image", gray)
cv2.waitKey(0)

cv2.imwrite(star_file, gray)

exit()


params = cv2.SimpleBlobDetector_Params()

params.minThreshold = 200 
params.maxThreshold = 255 

params.filterByArea = True
params.minArea = 3 
#params.maxArea = 100

params.filterByConvexity = False 
#params.minConvexity = .87
#params.maxConvexity = 1
#params.minCircularity= .1

detector = cv2.SimpleBlobDetector_create(params)

keypoints = detector.detect(gray)

im_with_points = cv2.drawKeypoints(gray, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imshow("Image", im_with_points)
cv2.waitKey(0)


exit()
thresh = 150 
maxValue=255

th, dst = cv2.threshold(gray, thresh, maxValue, cv2.THRESH_BINARY)

#(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
#cv2.circle(gray, maxLoc, 5, (255, 0, 0), 2)
#view_mask = cv2.convertScaleAbs(gray)
#exit()

cv2.imshow("Image", dst)
cv2.waitKey(0)
#(contours, hierarchy, x) = cv2.findContours(img_filt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#print (len(contours))

#for c in contours:
#   print (c)
   #cv2.drawContours(img_filt, [c], -1, (0, 255,0), 2)
   #cv2.imshow("Image", img_filt)
   #cv2.waitKey(0)

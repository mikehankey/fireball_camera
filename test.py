import cv2
import numpy as np

jpg_file = "20161122004024.jpg"
star_upper = np.array([255, 255, 255])
star_lower = np.array([50, 50, 50])
img_filt = cv2.imread(jpg_file)
gray = cv2.cvtColor(img_filt, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (1,1), 0)
#hsv = cv2.cvtColor(img_filt, cv2.COLOR_BGR2HSV)
#mask = cv2.inRange(hsv, star_lower, star_upper)
#print (mask)

params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 100 
params.maxThreshold = 200
params.filterByArea = True
params.minArea =  1
params.maxArea = 20
params.filterByConvexity = True
params.minConvexity = .87
params.minCircularity= .1
detector = cv2.SimpleBlobDetector_create(params)

keypoints = detector.detect(img_filt)

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

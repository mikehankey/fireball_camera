#!/usr/bin/python3

import cv2
assert cv2.__version__[0] == '3', 'The fisheye module requires opencv version >= 3.0.0'
import numpy as np
import os
import glob
import sys

objpoints = []
imgpoints = []
pattern_size = 6,3
subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
#calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_FIX_SKEW

#img_file = "/mnt/ams2/cal/20180922105200-6.jpg"
img_file = sys.argv[1]
#data_file = "/mnt/ams2/cal/20180922105200-6-star-dist-data.txt"
data_file = img_file.replace(".jpg", "-star-dist-data.txt")

lines = ""
fp = open(data_file)
for line in fp:
   lines = lines + line
exec(lines)
#print(str(star_dist_data))
#pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
   
#oa= np.zeros((1, 3), dtype=np.float32)
#ia= np.zeros((1, 2), dtype=np.float32)
oa = []
ia = []
for star, x2,y2,x1,y1 in star_dist_data:
   
   print(star)

   #oa.append((x2-x1,y2-y1,0))
   oa.append((x1-x2,y1-y2,0))
   ia.append(((x2,y2)))
   #oa.append(((x2-x1,y2-y1,0)))
   #ia.append(((x2,y2)))

oa = np.array([oa], dtype= np.float32)
ia = np.array([ia], dtype=np.float32)

objpoints.append(oa)
imgpoints.append(ia)


print("OBJ:", objpoints)
print("IMG:", imgpoints)
print("OBJ SHAPE:", objpoints[0].shape)
print("IMG SHAPE:", imgpoints[0].shape)
rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (1920, 1080), None, None)

img = cv2.imread(img_file)

h,  w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))
print("ROI", roi)
dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)
print ("CAMERA MATRIX: " + str(camera_matrix))
print ("2" + str(newcameramtx))
# crop and save the image
x, y, w, h = roi
print (x,y,w,h)
#dst = dst[y:y+h, x:x+w]

outfile = img_file.replace(".jpg", "_undistorted.jpg")
outfile2 = img_file.replace(".jpg", "_undistorted2.jpg")
dist_co_file = img_file.replace(".jpg", "_dist_co.txt")
print('Undistorted image written to: %s' % outfile)
cv2.imwrite(outfile, dst)
fpo = open(dist_co_file, "w")
fpo.write("dist_coefs=" + str(dist_coefs))
print (dist_coefs)
#exit()


N_OK = len(objpoints)
K = np.zeros((3, 3))
D = np.zeros((4, 1))

N_OK = len(objpoints)
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
print ("LEN: ", len(objpoints))
cv2.fisheye.calibrate( objpoints, imgpoints, (1080,1920), K, D, rvecs, tvecs)
        #calibration_flags,
        #(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
print("Found " + str(N_OK) + " valid images for calibration")
#print("DIM=" + str(_img_shape[::-1]))
print("K=np.array(" + str(K.tolist()) + ")")
print("D=np.array(" + str(D.tolist()) + ")")

#
img = cv2.imread(img_file)
h,w = img.shape[:2]
DIM = 1920,1080
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
cv2.imwrite(outfile2, undistorted_img)

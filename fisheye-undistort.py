#!/usr/bin/python3

import cv2
import numpy as np
import sys

# You should replace these 3 lines with the output in calibration step
DIM=1920,1080
K=np.array([[611.1549814728781, 0.0, 539.5], [0.0, 611.1549814728781, 959.5], [0.0, 0.0, 1.0]])
D=np.array([[0.0], [0.0], [0.0], [0.0]])
def undistort(img_path, DIM, K, D):
    img = cv2.imread(img_path)
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.imwrite("/mnt/ams2/cal/test.jpg", undistorted_img)
if __name__ == '__main__':
    for p in sys.argv[1:]:
        undistort(p)

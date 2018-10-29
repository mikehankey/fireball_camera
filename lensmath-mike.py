#!/usr/bin/python3 

import math
import numpy as np

def calc_dist(x1,y1,x2,y2):
   dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
   return(dist)

def compute_r(x,y):
   # r^2 = x^2 + y^2
   return(math.sqrt(iix**2 + iiy**2))

def compute_k1_k2(x1 = [],y1 = [],x2 = [],y2 = [],r = []):
   # x2[0] = (1 + (k1 * r[0]) ** 2  + (k2 * r[0] ** 4)) * x1[0] 
   # x2[1] = (1 + (k1 * r[1]) ** 2  + (k2 * r[1] ** 4)) * x1[1] 
   # 
   # [(x2[0] / x1[0]) - 1 = (r[0] ** 2) * r[0] ** 4) * k1
   # [(x2[1] / x1[1]) - 1 = (r[1] ** 2) * r[1] ** 4) * k2
   #
   # [((x2[0] / x1[0]) - 1) / (r[0] ** 2) * r[0] ** 4) = k1]
   # [((x2[1] / x1[1]) - 1) / (r[1] ** 2) * r[1] ** 4) = k2]
   expression = "((x2 / x1) - 1) / ((r ** 2) * r ** 4)) = k1

def undistort_point(x,y):
   k = (8.79265391e-40, 1.58290511e-41, 2.96524095e-20, 5.33820064e-22)
 

w = 1920
h = 1080

center_x =  w / 2
center_y =  h / 2

ix = []
iy = []
cx = []
cy = []
r = []
aa = []
rr = []
cpr = []
ipr = []
epr = []

for star_name, iix, iiy, ccx, ccy in star_dist_data:
   ix.append (iix)
   iy.append (iiy)
   cx.append (ccx)
   cy.append (ccy)

   c_dist = calc_dist(center_x, center_y, ccx,ccy)
   i_dist = calc_dist(center_x, center_y, iix,iiy)
   e_dist = calc_dist(ccx, ccy, iix,iiy)
   cpr.append(c_dist)
   ipr.append(i_dist)
   epr.append(e_dist)

   r.append (math.sqrt(iix**2 + iiy**2) )
   r_val = math.sqrt(iix**2 + iiy**2) 
   aa.append([ccx/iix - 1])
   rr.append([(r_val**2)*(r_val**4)])

for n in range(0, len(cpr) -1):
   print(cpr[n],ipr[n],epr[n],epr[n]/cpr[n])
exit()

A = np.array(aa)
B = np.array(rr)
print ("A:", A)
print ("B:", B)
z = np.linalg.lstsq(A,B)
#z = np.linalg.solve(A,B)
print ("Z:", z)


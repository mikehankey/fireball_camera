#!/usr/bin/python3 
# 
# implementation of equations found on this post about lens distortion
# https://math.stackexchange.com/questions/302093/how-to-calculate-the-lens-distortion-coefficients-with-a-known-displacement-vect 
#  

import sys
import math
import numpy as np
#import lmfit

def compute_r(x,y):
   # function to compute r as described here:
   # r^2 = x^2 + y^2
   return(math.sqrt(x**2 + y**2))

def undistort_point(x1,y1,k):
   xc = 1920 / 2
   yc = 1080 / 2
   r = compute_r_new(x1,y1)
   ksum = 1 + (k[0] * r ** 2) + (k[1] * r ** 4)  + (k[2] * r ** 6) + (k[3] * r ** 8)
   ksum = k[0] + (k[1] * r) + (k[2] * r ** 2) + (k[3] * r ** 4)
   print ("KSUM: ", ksum)
   xtop = x1 - xc
   ytop = y1 - yc
 
   xu = x1 + (xtop / ksum)
   yu = y1 + (ytop / ksum)
   xchange = (xtop / ksum)
   ychange = (ytop / ksum)

   print ("X1,X2:", x1, xu)
   print ("Y1,Y2:", y1, yu)
   print ("XY Change:", xchange, ychange)
   psum = 0


def compute_r_new(x,y):
   xc = 1920 / 2
   yc = 1080 / 2
   r = math.sqrt( ((x - xc) ** 2) + ((y - yc) ** 2))
   return(r)

def undistort_point_old(x,y,k):
   # method described here: https://www.mathworks.com/products/demos/symbolictlbx/Pixel_location/Camera_Lens_Undistortion.html 
   print ("Undistort:", k)
   print ("K:", k)
   #k = (8.79265391e-40, 1.58290511e-41, 2.96524095e-20, 5.33820064e-22)
   r = compute_r_new (x,y) 
  
   x2 = x * (1 + k[0] * r ** 2 + k[1] * r ** 4) + (2 * k[2] * x * y) + k[3] * (r ** 2 + 2 * x ** 2)
   y2 = y * (1 + k[0] * r ** 2 + k[1] * r ** 4) + (2 * k[2] * x * y) + k[3] * (r ** 2 + 2 * y ** 2)
   xfac =  (1 + k[0] * r ** 2 + k[1] * r ** 4) + (2 * k[2] * x * y) + k[3] * (r ** 2 + 2 * x ** 2)
   yfac =  (1 + k[0] * r ** 2 + k[1] * r ** 4) + (2 * k[2] * x * y) + k[3] * (r ** 2 + 2 * y ** 2)
   print ("x = ", x)
   print ("y = ", y)
   print ("x2 = ", x2)
   print ("y2 = ", y2)
   print ("R = ", r)
   print ("XFactor = ", xfac)
   print ("YFactor = ", yfac)


def method_two (star_dist_data): 
   As = []
   Bs = []

def method_one (star_dist_data):
   
   # define lists needed for the equation
   As = []
   Bs = []
   
   # loop over star data and compute r, A & B and build the A & B lists
   for star_name, iix, iiy, ccx, ccy in star_dist_data:
      # compute R per specs on stackexchange example
      r = compute_r_new(iix,iiy)
   
      # compute the A part of the equation
      A = (r ** 2) * (r **4) 
      # compute the B part of the equation
      B = ccx - iix 

      # add the As to the list
      As.append((A))
      # add the Bs to the list
      Bs.append((B))
   
      # Now do it for the ys too
      # compute the A part of the equation
      #A = (r ** 2) * (r **4)
      # compute the B part of the equation
      #B = ccy/iiy -1
      # add the As to the list
      #As.append((A))
      # add the Bs to the list
      #Bs.append((B))
   
   
   
   # convert As & Bs to the proper numpy format matrix 
   npAs = np.column_stack([np.ones(len(As)), As])
   npBs = np.column_stack([np.ones(len(Bs)), Bs])
   
   # solve Ax = B with least square fit
   result, _, _, _ = np.linalg.lstsq(npAs,npBs,rcond=None)
   
   print ("YO", result)
   
   # print out result
   k = []
   k.append(result[0][0])
   k.append(result[0][1])
   k.append(result[1][0])
   k.append(result[1][1])
   # test undistort
   #undistort_point_old(100,900,k)
   #undistort_point(100,900,k)
   #undistort_point(5,900,k)
   undistort_point(1918,1000,k)
   undistort_point(970,550,k)
   
# read input file from command line
star_file = sys.argv[1]

# open input file expecting an array defining the star_dist_data
fp = open(star_file, 'r')
   
for line in fp:
   # execute the code in the file which will populate the star_dist_data array
   exec(line, locals(), globals())
fp.close()

method_one(star_dist_data)
#method_two(star_dist_data)

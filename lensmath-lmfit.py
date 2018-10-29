#!/usr/bin/python3 

import sys
import math
import numpy as np
import lmfit

def compute_r(x,y):
   # r^2 = x^2 + y^2
   return(math.sqrt(iix**2 + iiy**2))


w = 1920
h = 1080

center_x =  w / 2
center_y =  h / 2

star_file = sys.argv[1]
print (star_file)
fp = open(star_file, 'r')
#print (star_file)
for line in fp:
   exec(line)
fp.close()

ix = []
iy = []
cx = []
cy = []

x1 = 1 
x2 =1 
y1 =1 
y2 =1 
r =1 
data = []
for star_name, iix, iiy, ccx, ccy in star_dist_data:
   data.append([iix,iiy,ccx,ccy])

k1 = (x2 / x1) - 1 / (r ** 2) * r ** 4
model = lmfit.models.ExpressionModel("(x2 / x1) - 1 / (r ** 2) * r ** 4", independent_vars=['x1', 'x2', 'r']) 
params = model.make_params(x1=0,y1=0,x2=0,y2=0,r=0)
fit = model.fit(data, params, x1=x1, x2=x2,r=r)
print (fit.nfev)
print (fit.ndata)
print (fit.nvarys)
print (fit.chisqr)
print (fit.redchi)
print (fit.aic)
print (fit.bic)

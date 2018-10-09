#!/usr/bin/python3 

import sys
from sympy import *
import math
import numpy as np

def calc_dist(x1,y1,x2,y2):
   dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
   return(dist)

def compute_rs(x1,y1,x2,y2,center_x,center_y):
   r = calc_dist(x1,y1,center_x,center_y)      
   R = calc_dist(x2,y2,center_x,center_y)      
   return(r,R)

def compute_k(x1,y1,x2,y2):
   debug = 0
   #print ("Compute K")
   k1 = float(0)
   k2 = float(0)         
   r = math.sqrt((x1**2) + (y1**2))
   r2 = r ** 2
   r4 = r ** 4
   if debug == 1:
      print ("X1: ", x1)
      print ("Y1: ", y1)
      print ("X2: ", x2)
      print ("Y2: ", y2)
      print ("R: ", r)
      print ("R2: ", r2)
      print ("R4: ", r4)
      print(x1,y1,x2,y2)
   print(str(x2) + " " +  str(y2) + " " + str(x1) + " " + str(y1))

   #1 + (k1 * r2) + (k2 * r4) = math.sqrt((x2 ** 2 + y2 ** 2) / r2))
   right_side = math.sqrt(x2 ** 2 + y2 ** 2 / r2)
   left_side = "k1 * " + str(r2) + " +  k2 * " + str(r4) 
   if debug == 1:
      print (str(left_side) + " = " + str(right_side))

   #step 1
   right_side2a = str(r4) + "  * b +"
   right_side2b = math.sqrt(x2 ** 2 + y2 ** 2 / r2) 
   left_side2 = str(r2) + " * a " 

   if debug == 1:
      print (str(left_side2) + " = " + str(right_side2a) + " " + str(right_side2b))

   # step 2
   left_side3 = "a = "
   right_side3a = r4 / r2 
   right_side3b = right_side2b / r2

   right_side3 = str(right_side3a) + " * b + " + str(right_side3b) 

   if debug == 1:
      print (left_side3 + right_side3)
      print ("")

   return(right_side3a, right_side3b,r)


star_file = sys.argv[1]
print (star_file)
fp = open(star_file, 'r')
#print (star_file)
for line in fp:
   #print(line) 
   exec(line)
fp.close()
#print (star_dist_data)

w = 1920
h = 1080

center_x =  w / 2
center_y =  h / 2

ass = []
bs = []
rs = []
for star_name, iix, iiy, ccx, ccy in star_dist_data:
   #a,b,r = compute_k(iix,iiy,ccx,ccy)
   r,R = compute_rs(iix,iiy,ccx,ccy,center_x,center_y)
   equation = "Eq(" + str(R) + " = (a * (" + str(r) + " ** 3) + b * (" + str(r) + " ** 2) + c * (" + str(r) + " + d)) * " + str(r)
   print(equation)

   #print (a,b,r)
   #ass.append(a)
   #bs.append(b)
   #rs.append(r)

exit()

#equation = "system = [\n"
equation = ""
equations = []
text_exp = []
for i in range(0,len(ass)-1):
   equation = "Eq(" + str(ass[i]) + "*y + " + str(bs[i]) + ",x)"
   text_exp.append("r=" + str(rs[i]))
   equations.append(equation)

q = 0
x, y = symbols(['x', 'y'])
for equation in equations:
   exec_str = ""
   if q % 2 == 0 and q < len(equations) -1:
      exec_str = exec_str + "system = ["
      exec_str = exec_str + str(equations[q]) + ","
      exec_str = exec_str + " " + str(equations[q+1])
      exec_str = exec_str + "]\n"
      exec_str = exec_str + "soln = solve(system, [x,y])\n"
      #exec_str = exec_str + "print(text_exp[q])\n"
      #exec_str = exec_str + "print(text_exp[q-1])\n"
      exec_str = exec_str + "print(soln)\n"

   q = q + 1
   #print (exec_str)
   exec(exec_str)      

#from sympy import *
#x, y = symbols(['x', 'y'])
#a = 827019.0428561743 * b + 0.0009337078855767633
#a = 1146749.0000000002 * b + 0.00021126274484225226
#system = [
#    Eq(827019.0428561743*y + 0.0009337078855767633, x),
#    Eq(1146749.0000000002*y + 0.00021126274484225226, x)
#]
#soln = solve(system, [x, y])
#print(soln)


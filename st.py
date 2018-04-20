from math import atan, tan
import numpy as np
from numpy import ones,vstack
from numpy.linalg import lstsq, solve
points = [(438,405),(437,405),(437,407),(438,408),(437,409)]
#points = [(438,405),(437,407),(437,409)]

#angle = atan(a1) #- atan(b1)
#print (angle)
#print (tan(angle))
#print(atan(points[0])

def is_straight(points):
   last_angle = None
   total = len(points)
   print ("TP", total)
   passed = 0
   for i in range(1,total): 
      print(i)
      angle = find_angle(points[0][0], points[0][1], points[i][0], points[i][1])
      print (points[0][0], points[0][1], points[i][0], points[i][1], angle)
      if last_angle is not None:
         if (last_angle - 1) < angle < (last_angle + 1):
            passed = passed + 1
            print("passed")
         else:
            print("failed")

      last_angle = angle

   match_percent = passed / (total - 2)
   print (match_percent)
    
def find_angle(x1,x2,y1,y2):
   if x2 - x1 != 0:
      a1 = (y2 - y1) / (x2 - x1)
   else:
      a1 = 0
   angle = atan(a1)
   return(angle)

is_straight(points)

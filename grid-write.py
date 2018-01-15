
import numpy as np
import scipy.interpolate
import cv2



def draw_line(az_grid, alt_cords):
   alt_cords_np = np.array(alt_cords)
   try:
      f = scipy.interpolate.interp1d(alt_cords_np[:, 0], alt_cords_np[:, 1], kind='quadratic')

      #New points will be evenly distributed along x
      new_x = np.linspace(np.min(alt_cords_np[:, 0]), np.max(alt_cords_np[:, 0]), 10)
      new_y = f(new_x)

      new_coords = np.vstack([new_x, new_y]).T
   except:
      print ("Failed INT")
      new_coords = alt_cords_np
   pts = new_coords
   #pts = pts.reshape((-1,1,2))
   ret = cv2.polylines(az_grid, [np.int32(pts)], 0, (255,255,255), 1,1)
#   print (ret)


def load_az_grid_borders():
   file = open('azgrid.txt', "r")
   lc = 1
   grid_points = []
   for line in file:
      type, x,y,az,alt = line.split(" ")
      x = int(float(x))
      y = int(float(y))
      az = int(float(az))
      alt = int(float(alt))
      grid_points.append((type,x,y,az,alt))
   #print (grid_points)
   return(grid_points)

def load_az_grid():

   file = open('azgrid.txt', "r")
   lc = 1
   grid_points = []
   for line in file:
      junk = line.split(" ")
      az_line = 0
      alt_line = 0
      type, x,y,az,alt = line.split(" ")
      x = int(float(x))
      y = int(float(y))
      az = int(float(az))
      alt = int(float(alt))
      grid_points.append((type,x,y,az,alt))
   return(grid_points)

 
def group_points(grid_points, mytype, min,max):
   az_cords_left = []
   alt_cords_left = []
   az_cords_right = []
   alt_cords_right = []
   for line in grid_points:
      type, x, y, az, alt = line
      if type == "LEFT-AZ":
         if int(min) <= int(float(az)) <= int(max):
            az_cords_left.append([int(x),int(y)])
      if type == "RIGHT-AZ":
         if int(min) <= int(float(az)) <= int(max):
            az_cords_right.append([int(x),int(y)])
      if type == "LEFT-ALT":
         if int(min) <= int(float(alt)) <= int(max):
            alt_cords_left.append([int(x),int(y)])
      if type == "RIGHT-ALT":
         if int(min) <= int(float(alt)) <= int(max):
            alt_cords_right.append([int(x),int(y)])

   if mytype == "LEFT-ALT": 
      return(alt_cords_left)
   if mytype == "RIGHT-ALT": 
      return(alt_cords_right)
   if mytype == "LEFT-AZ": 
      return(az_cords_left)
   if mytype == "RIGHT-AZ": 
      return(az_cords_right)





img_file = "/var/www/html/out/cal/astrometry/20171230014758-1.jpg"
az_grid = cv2.imread(img_file)
az_grid_gray = cv2.cvtColor(az_grid, cv2.COLOR_BGR2GRAY)

grid_points = load_az_grid_borders()

left_points = group_points(grid_points, "LEFT-ALT", 30-1, 30+1)
avg_left_x = np.average(left_points, axis = 0)
print ("AVG LEFT SIDE X,Y FOR ELEVATION 30:", avg_left_x)

right_points = group_points(grid_points, "RIGHT-ALT", 30-1, 30+1)
avg_right_x = np.average(right_points, axis = 0)
print ("AVG RIGHT SIDE X,Y FOR ELEVATION 30:", avg_right_x)

exit()
grid_points = load_az_grid()

grid_points = np.array(grid_points)

#y = 50
#points = group_points(grid_points, "y", y-1, y+1)
#print ("POINTS:", points)
#draw_line(az_grid, points)
#draw_line(az_grid, [[0,0],[100,100]])


for x in range (0,365):
   if x % 10 == 0:
      points = group_points(grid_points, "x", x-1, x+1)
      if len(points) >= 3:
         print ("X:", x, points)
         draw_line(az_grid, points)

for y in range (0,90):
   if y % 10 == 0:
      points = group_points(grid_points, "y", y-1, y+1)
      if len(points) >= 1:
         print ("Y:", y, points)
         draw_line(az_grid, points)







cv2.imwrite("azgrid_cv.png", az_grid)

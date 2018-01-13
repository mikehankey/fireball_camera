import re
import math
import fitsio
import sys
from amscommon import read_config
import subprocess
import os
import numpy as np
#from tkinter import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
from PIL import ImageEnhance
#from tkinter.filedialog import askopenfilename
#from tkinter.ttk import *
import cv2

import matplotlib.pyplot as plt
import os
from astropy.io import fits
from astropy.wcs import WCS
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

def parse_file_date(full_file_name):
   stuff = full_file_name.split("/")
   file_name = stuff[-1]

   year = file_name[0:4]
   month = file_name[4:6]
   day = file_name[6:8]
   hour = file_name[8:10]
   min = file_name[10:12]
   sec = file_name[12:14]
   date_str = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec
   return(date_str)


def find_radec_from_xy_pya( x,y, W):

   target = SkyCoord.from_pixel(x,y,W)
   ra = target.ra
   dec = target.dec
   #print(ra,dec)
   radd = convert_dms_to_ddms(str(ra))
   decdd = convert_dms_to_ddms(str(dec))
   #print(radd,decdd)
   return(ra,dec,radd,decdd)

def characterize_altaz(x1,y1,x2,y2,W,location,cal_time):
   (calt,caz) = convert_xy_to_altaz(x1,y1,W,location,cal_time)
   (tlalt,tlaz) = convert_xy_to_altaz(x2,y2,W,location,cal_time)
   # Diff in degrees
   if calt > tlalt:
      vd_alt_diff = calt - tlalt
   else:
      vd_alt_diff = tlalt - calt
   if caz > tlaz:
      vd_az_diff = caz - tlaz
   else:
      vd_az_diff = tlaz - caz
   
   # VD in pixels
   vd_dist = find_xy_distance(x1,y1,x2,y2)
   az_pp = vd_az_diff / vd_dist
   alt_pp = vd_alt_diff / vd_dist

   #print ("AZ/ALT AZ PER PIXEL X,Y: ", az_pp, alt_pp, x1,y1,x2,y2)
   return(az_pp, alt_pp)
def find_xy_distance(x1,y1,x2,y2):
   #print ("x2,x1,y2,y1", x2,x1, y2,y1)
   d = math.sqrt((x2- x1)**2 + (y2 - y1) **2)

   #print( "SQRT ", (x2 - x1)**2, "+", (y2-y1)**2)
   #print ("XY, Distance is: ",x1,y1,x2,y2, d)
   return(d)

def draw_az_grid(file):
   first_list = []

   cam_num = 1
   config_file = "conf/config-" + str(cam_num) + ".txt"
   config = read_config(config_file)
   loc_lat = config['device_lat']
   loc_lon = config['device_lng']
   loc_alt = config['device_alt']

   W = WCS(file)
   image_file = file.replace("-sd.new", ".jpg")
   cal_time = parse_file_date(image_file)


   location = EarthLocation.from_geodetic(float(loc_lon)*u.deg,float(loc_lat)*u.deg,float(loc_alt)*u.m)

   az_grid = cv2.imread(image_file)
   az_grid_np = cv2.cvtColor(az_grid, cv2.COLOR_BGR2GRAY)

   #azpp1, altpp1 = characterize_altaz(0,0,320,180,W, location, cal_time)
   #azpp2, altpp2 = characterize_altaz(0,0,0,360,W, location, cal_time)
   #azpp3, altpp3 = characterize_altaz(0,0,640,0,W, location, cal_time)
   mypass = 0
   print ("Grid y is ", az_grid_np.shape[0])
   print ("Grid x is ", az_grid_np.shape[1])

   last_az_pp = 0
   last_at_pp = 0
   avg_az_pp = 0
   avg_at_pp = 0
   az_pp = 0
   at_pp = 0
   last_alt= 0
   last_az  = 0
   last_x  = None 
   last_y  = None 

   for x in range(0,az_grid_np.shape[1]):
      if (x % 50 == 0) :
         for y in range(az_grid_np.shape[0]):
            if mypass >= 1:
               mypass = mypass - 1
               #print ("pass is ", mypass, "skipping")
               continue
            else:
               if (y % 1 == 0) :
                  #print("TRACE: ", x,y,cal_time)
                  (oalt,oaz) = convert_xy_to_altaz(x,y,W,location,cal_time)
                  remat = 10 - (oalt % 10)
                  remaz = 10 - (oaz % 10)
                  #print ("REMAT/REMAZ: ", remat, remaz)
                  if remat < .7 or remat > 9.3:
                     print ("**** x,y,az,alt", remat, x,y,oaz,oalt)
                     az_grid[y,x] = [255,255,255]
                     mypass = 20
                  else:
                  #   print ("remat, x,y,az,alt", remat,x,y,oaz,oalt)
                     if avg_at_pp != 0:
                        skip = remat / avg_at_pp 
                        #print ("skip = ", skip)
                        mypass = skip * .5
                     if remat > 7:
                        mypass = 0 

                  if last_x != None:
                     if abs(x - last_x) != 0:
                        az_pp = abs(oaz - last_az) / abs(x - last_x)
                     else:
                        az_pp = 0
                     if abs(y - last_y) != 0:
                        at_pp = abs(oalt - last_alt) / abs(y - last_y)
                     else:
                        at_pp = 0
                     #print ("AZ/EL Per Pixel = ", last_az_pp, last_at_pp)
                     if avg_az_pp == 0:               
                        avg_az_pp = az_pp
                     avg_az_pp = (avg_az_pp + last_az_pp + az_pp) / 3
                     if avg_at_pp == 0:               
                        avg_at_pp = at_pp
                     avg_at_pp = (avg_at_pp + last_at_pp + at_pp) / 3
              
                  last_az_pp = az_pp  
                  last_at_pp = at_pp  
                  last_az = oaz
                  last_alt = oalt
                  last_x = x
                  last_y = y 



   for y in range(0,az_grid_np.shape[0]):
      if (y % 50 == 0) :
         for x in range(az_grid_np.shape[1]):
            if mypass >= 1:
               mypass = mypass - 1
               #print ("pass is ", mypass, "skipping")
               continue
            else:
               if (x % 1 == 0) :
                  (oalt,oaz) = convert_xy_to_altaz(x,y,W,location,cal_time)
                  remat = 10 - (oalt % 10)
                  remaz = 10 - (oaz % 10)
                  #print ("REMAT/REMAZ: ", remat, remaz)
                  if remaz < .7 or remaz > 9.3:
                     print ("**** x,y,az,alt", x,y,oaz,oalt)
                     az_grid[y,x] = [255,255,255]
                     mypass = 20
                  else:
                     #print ("remaz, x,y,az,alt", remaz,x,y,oaz,oalt)
                     if remaz > 8:
                        mypass = 20
                     if remaz < 8 and remaz > 5:
                        mypass = 8 
                     if remaz < 5 and remaz > 3:
                        mypass = 4 
                     if remaz < 3:
                        mypass = 0 






   cv2.imwrite("azgrid.png", az_grid)      
      
      
def is_ten_close(x,y,alt,az, W, location, cal_time):
   alt_rem = alt % 10
   az_rem = az % 10
   if alt_rem > 5:
      print ("the next marker up in elevation is down in y from here, decrease y to go higher in elevation")
      direction = "up"
      next_y = y - 10
      if next_y < 0:
         print ("that way is off the frame!, need to go the other direction.")
         direction = "down"
   else:
      print ("the next marker down in elevation is up in y from here, increase y to go lower in elevation")
      direction = "down"
      next_y = y + 10
      if next_y > 360:
         print ("that way is off the frame!, need to go the other direction.")
         direction = "up"

   if az_rem > 5:
      print ("the next marker up in az is right increase x to go higher from here, ")
      azdirection = "right"
      next_x = x + 10
      if next_x > 640:
         print ("that way is off the frame!, need to go the other direction.")
         azdirection = "left"
   else:
      print ("the next marker down in az is left, decrease x  to go lower in azimuth ")
      azdirection = "left"
      next_x = x - 10
      if next_x < 0:
         print ("that way is off the frame!, need to go the other direction.")
         azdirection = "right"

   alt_rem = alt % 10
   az_rem = az % 10

   if alt_rem > 5:
      alt_rem = 10 - alt_rem
      dalt = alt + alt_rem
   else: 
      dalt = alt - alt_rem


   if az_rem > 5:
      az_rem = 10 - az_rem
      daz = az + az_rem
   else:
      daz = az - az_rem

   galt = abs(dalt - alt)
   gaz = abs(daz - az)

   if direction == "down":   
      galt = galt * -1
   if azdirection == "right":   
      gaz = gaz * -1

   print ("Current Alt is: ", alt)
   print ("Current AZ is: ", az)
   print ("Desired Alt is: ", dalt)
   print ("Desired AZ is: ", daz)
   print ("Elevation direction is: ", direction)
   print ("Azimuth direction is: ", azdirection)
   print ("Guess shift alt,az: ", galt, gaz)
   gx = gaz * 7.75
   gy = galt * 7.75
   print ("Guess shift in pixels x,y", gx, gy)
   new_x = x - gx 
   new_y = y - gy 
   (alt,az) = convert_xy_to_altaz(new_x,new_y,W,location,cal_time)
   print ("New alt,az,x,y:", int(alt),int(az), int(new_x), int(new_y))

def guess(x,y,alt,az,azpp,altpp,W,location,cal_time):
   alt_rem = alt % 10
   az_rem = az % 10

   #print ("REM AZ,ALT", int(az_rem), int(alt_rem))

   if alt_rem > 5:
      alt_rem = 10 - alt_rem
      dalt = alt + alt_rem
      ff = 1
      if alt > dalt:
         galt = abs(alt - dalt) * ff
      else:
         galt = abs(dalt - alt) * ff
   else:
      ff = -1
      dalt = alt - alt_rem
      if alt > dalt:
         galt = abs(alt - dalt) * ff
      else:
         galt = abs(dalt - alt) * ff

   if az_rem > 5:
      az_rem = 10 - az_rem
      daz = az + az_rem
      ff = 1
      if az > daz:
         gaz = abs(az - daz) * ff
      else: 
         gaz = abs(daz - az) * ff
   else:
      daz = az - az_rem
      ff = -1
      if az > daz:
         gaz = abs(az - daz) * ff
      else: 
         gaz = abs(daz - az) * ff



   gx = gaz / azpp
   gy = galt / altpp
   print ("1st AZ,ALT PP", azpp,altpp)

   azpp2, altpp2 = characterize_altaz(x,y,x+50,y+50,W, location, cal_time)

   gx = gaz / azpp2
   gy = galt / altpp2

   print ("2nd AZ,ALT PP", azpp2,altpp2)
   print ("Desired AZ/ALT", daz,dalt)
   print ("AZ,ALT Change Needed: ", gaz, galt)
   print ("X,Y Shift Recommended: ", gx, gy)
   return(gx,gy)

def find_tens_on_line(mx, my, W, location, cal_time):
   (alt,az) = convert_xy_to_altaz(mx,my,W,location,cal_time)

   print(alt,az)
   is_ten_close(mx,my,alt,az, W, location, cal_time)
   #for x in range(az_grid_np.shape[1]):
    

def convert_xy_to_altaz(x,y, W,location,cal_time):
   (ra, dec, radd, decdd) = find_radec_from_xy_pya(x, y, W)
   target = SkyCoord(ra=float(radd)*u.degree, dec=float(decdd)*u.degree, frame='icrs')
   altaz = target.transform_to(AltAz(location=location, obstime=Time(cal_time)))
   alt = convert_dms_to_ddms(str(altaz.alt))
   az = convert_dms_to_ddms(str(altaz.az))
   return(alt,az)

def convert_dms_to_ddms(dms):
   #print(dms)
   temp = str(dms)
   d,m,s,x = re.split("d|m|s", temp)
   #print (d,m,s)
   s = float(s)/60
   m = (int(m)/60) + s
   d = int(d) + float(m)
   return(d)



file = "/var/www/html/out/cal/astrometry/20171230014758-1-sd.new"
draw_az_grid(file)
#find_radec_from_xy_pya(W, 0,0)

#!/usr/bin/python3

# 20180922105200-6-indx.xyls -- catalog stars x,y
# 20180922105200-6.axy -- image stars x,y
import fitsio 
import sys
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import math

def calc_dist(x1,y1,x2,y2):
   dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
   return(dist)


def calc_angle(pointA, pointB):
  changeInX = pointB[0] - pointA[0]
  changeInY = pointB[1] - pointA[1]
  ang = math.degrees(math.atan2(changeInY,changeInX)) #remove degrees if you want your answer in radians
  if ang < 0 :
     ang = ang + 360
  return(ang)

def dump_fits(filename):
   h = fitsio.read_header(filename, ext=1) 
   n_entries = h["NAXIS2"] 
   fits = fitsio.FITS(filename, iter_row_buffer=1000) 
   points = []
   for i in range(n_entries): 
      p = fits[1][i]
      if filename == image_filename:
         mag = p[0][2]
         if int(mag) > 10:
            #print ("MAG:", mag)
            x =  p[0][0]
            y =  p[0][1]
            points.append((x,y))
      else:
         x =  p[0][0]
         y =  p[0][1]
         points.append((x,y))
   return (points)


#catalog_filename = sys.argv[1] 
#image_filename = sys.argv[2] 

def find_closest_match(cx,cy, img_points, w, h):
   matches = []
   cat_center_dist = int(calc_dist(cx,cy,w/2,h/2))
   cat_center_ang = int(calc_angle((h/2,w/2),(cy,cx)))
   for x,y in img_points:
      if x -200 < cx < x + 200 and y - 200 < cy < y + 200:
         img_center_dist = int(calc_dist(x,y,w/2,h/2))
         img_center_ang = int(calc_angle((h/2,w/2),(y,x)))
         img_cat_ang = int(calc_angle((cy,cx),(y,x)))
         if (cat_center_dist > 600) and (img_center_dist < cat_center_dist):
            draw.ellipse((x-5, y-5, x+5, y+5),  outline ='gray')
            matches.append((x,y))
   return(matches)

def find_best_match(cx,cy,matches,w,h,draw):
   print ("Looking to match catalog star : ", cx,cy)
   cat_center_dist = int(calc_dist(cx,cy,w/2,h/2))
   draw.ellipse((cx-5, cy-5, cx+5, cy+5),  outline ='green')
   extra_match = []
   for mx,my in matches:
      # image star to catalog star image
      img_cat_ang = int(calc_angle((my,mx),(cy,cx)))

      # center to star image
      img_cnt_ang = int(calc_angle((h/2,w/2),(my,mx)))

      # center to cat star image
      cat_cnt_ang = int(calc_angle((h/2,w/2),(cy,cx)))

      ang_diff1 = img_cat_ang - img_cnt_ang 
      if ang_diff1 < 0:
         ang_diff1 = ang_diff1 * -1
      ang_diff2 = img_cat_ang -cat_cnt_ang 
      if ang_diff2 < 0:
         ang_diff2 = ang_diff2 * -1
      img_cat_dist = int(calc_dist(cx,cy,mx,my))
      print ("   Angles (img->cat), (cnt->img), (cnt->cat): ", img_cat_ang, img_cnt_ang, cat_cnt_ang, ang_diff1, ang_diff2, img_cat_dist)
      extra_match.append((mx,my,ang_diff1))

   if len(extra_match) > 0:
      sorted_extra =  sorted(extra_match,key=lambda x: x[2])
      bx, by, bd = sorted_extra[0]
      draw.text((bx+5,by), str(bd), font=font, fill=(255,255,255,128))
      draw.line((cx,cy, bx,by), fill=128)
      #draw.line((cx,cy, w/2,h/2), fill="blue")
      draw.ellipse((bx-5, by-5, bx+5, by+5),  outline ='red') 

   return(draw)



catalog_filename = "/mnt/ams2/cal/20180922105200-6-indx.xyls"
image_filename = "/mnt/ams2/cal/20180922105200-6.axy"
cal_file = "/mnt/ams2/cal/20180922105200-6.jpg"
plot_out_file = "/mnt/ams2/cal/20180922105200-6-mike-plot.jpg"

plot_image = Image.open(cal_file)
draw = ImageDraw.Draw(plot_image)
font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12, encoding="unic" )

cat_points = dump_fits(catalog_filename)
img_points = dump_fits(image_filename)
np.asarray(cat_points)
np.asarray(img_points)
w,h =  plot_image.size
pc = 0
for x,y in cat_points:
   if pc < 100:
      matches = find_closest_match(x,y, img_points, w, h)
      draw = find_best_match(x,y,matches,w,h, draw)
   pc = pc + 1
draw.line((w/2,0, w/2,h), fill="white")
draw.line((0,h/2, w,h/2), fill="white")

plot_image.save(plot_out_file)


#   print("CAT:", x,y)
#   draw.ellipse((x-5, y-5, x+5, y+5),  outline ='green')
#   matches = find_closest_match(x,y, img_points, w, h)
#
#   mc = 0
#   for mx,my in matches:
#      draw.ellipse((mx-5, my-5, mx+5, my+5),  outline ='red') 
#      # image star to catalog star image
#      img_cat_ang = int(calc_angle((my,mx),(y,x)))
#
#      # center to star image
#      img_cnt_ang = int(calc_angle((h/2,w/2),(my,mx)))
#
#      # center to cat star image
#      cat_cnt_ang = int(calc_angle((h/2,w/2),(y,x)))
#
#      if (pc < 1 and mc < 10) :
#         print (pc, mc, "   Image To Cat Angle: ", img_cat_ang, "=" , my,mx,y,x)
#         print (pc, mc, "   Center to Image Angle: ", img_cnt_ang, "=" , h/2,w/2,my,mx)
#         print (pc, mc, "   Center to Cat Angle: ", img_cnt_ang, "=", h/2,w/2,y,x)
#         draw.text((mx+5,my), str(img_cat_ang) + "/" + str(cat_cnt_ang), font=font, fill=(255,255,255,128))
#         draw.line((x,y, mx,my), fill=128)
#         draw.line((x,y, w/2,h/2), fill=128)
#         draw.line((mx,my, ), fill=128)
#      mc = mc + 1
#   pc = pc + 1
#
##avg_star_xy = np.average(found_points, axis = 0)
##draw.text((avg_star_xy[0], avg_star_xy[1]), "X", font = font, fill=(255,255,255))
##draw.text((avg_star_xy[0]+15, avg_star_xy[1]), "Plate Center X,Y:" + str(int(avg_star_xy[0])) + "," + str(int(avg_star_xy[1])), font = font, fill=(255,255,255))
#plot_image.save(plot_out_file)

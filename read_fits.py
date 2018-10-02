#!/usr/bin/python3

# 20180922105200-6-indx.xyls -- catalog stars x,y
# 20180922105200-6.axy -- image stars x,y
import fitsio 
import sys
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

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
            print ("MAG:", mag)
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

def find_closest_match(cx,cy, img_points):
   print("Catalog X,Y: ", cx,cy)
   matches = []
   for x,y in img_points:
      if x -200 < cx < x + 200 and y - 200 < cy < y + 200:
         print ("match:", cx, cy, x,y)
         matches.append((x,y))
   return(matches)

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
for x,y in cat_points:
   print(x,y)
   draw.ellipse((x-5, y-5, x+5, y+5),  outline ='green')
   matches = find_closest_match(x,y, img_points)
   for mx,my in matches:
      draw.ellipse((mx-5, my-5, mx+5, my+5),  outline ='red') 


#avg_star_xy = np.average(found_points, axis = 0)
#draw.text((avg_star_xy[0], avg_star_xy[1]), "X", font = font, fill=(255,255,255))
#draw.text((avg_star_xy[0]+15, avg_star_xy[1]), "Plate Center X,Y:" + str(int(avg_star_xy[0])) + "," + str(int(avg_star_xy[1])), font = font, fill=(255,255,255))
plot_image.save(plot_out_file)

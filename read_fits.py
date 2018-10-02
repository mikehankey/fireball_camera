#!/usr/bin/python3

# 20180922105200-6-indx.xyls -- catalog stars x,y
# 20180922105200-6.axy -- image stars x,y
import fitsio 
import sys
import numpy as np

def dump_fits(filename):
   h = fitsio.read_header(filename, ext=1) 
   n_entries = h["NAXIS2"] 
   fits = fitsio.FITS(filename, iter_row_buffer=1000) 
   points = []
   for i in range(n_entries): 
      p = fits[1][i]
      x =  p[0][0]
      y =  p[0][1]
      points.append((x,y))
   return (points)


#catalog_filename = sys.argv[1] 
#image_filename = sys.argv[2] 

catalog_filename = "/mnt/ams2/cal/20180922105200-6-indx.xyls"
image_filename = "/mnt/ams2/cal/20180922105200-6.axy"
cat_points = dump_fits(catalog_filename)
img_points = dump_fits(image_filename)
np.asarray(cat_points)
np.asarray(img_points)


print (cat_points)
print (img_points)

#!/usr/bin/python3

# TODO STILL 
# PLOT / TRACK the catalog stars that didn't match
# FIND REFINED CENTER
# DETERMINE +/- error as factor of 100 px from center and then limit search on this
# save end resulting file as star_name,x1,y1,x2,y2,r,R
# make a 2nd attempt to find stars missed in the first pass. 
# aggregate multiple runs to find final solution. 
# determine / track az/el -> x,y for all runs (as an alternative calibration method)

import fitsio 
import sys
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import math

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

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

def dump_fits(filename, image_filename = ""):
   h = fitsio.read_header(filename, ext=1) 
   n_entries = h["NAXIS2"] 
   fits = fitsio.FITS(filename, iter_row_buffer=1000) 
   points = []
   for i in range(n_entries): 
      p = fits[1][i]
      if filename == image_filename:
         mag = p[0][2]
         if int(mag) > 8:
            #print ("MAG:", mag)
            x =  p[0][0]
            y =  p[0][1]
            points.append((x,y))
      else:
         x =  p[0][0]
         y =  p[0][1]
         # don't add if there is another star close by already on the list
         skip = 0
         for tx, ty in points:
           if tx -20 < x < tx +20 and ty -20 < y < ty + 20:
              #print ("skip star cause it is close to another one already.")
              skip = 1
         if skip == 0:
            points.append((x,y))
   return (points)


#catalog_filename = sys.argv[1] 
#image_filename = sys.argv[2] 

def find_closest_match(cx,cy, img_points, w, h, draw):
   matches = []
   cat_center_dist = int(calc_dist(cx,cy,w/2,h/2))
   cat_center_ang = int(calc_angle((h/2,w/2),(cy,cx)))
   for x,y in img_points:
      if cat_center_dist > 400:
         if x -100 < cx < x + 100 and y - 100 < cy < y + 100:
            img_center_dist = int(calc_dist(x,y,w/2,h/2))
            img_center_ang = int(calc_angle((h/2,w/2),(y,x)))
            img_cat_ang = int(calc_angle((cy,cx),(y,x)))
            if (cat_center_dist > 400) and (img_center_dist < cat_center_dist):
               draw.ellipse((x-5, y-5, x+5, y+5),  outline ='gray')
               matches.append((x,y))
      elif cat_center_dist <= 400:
         if x -10 < cx < x + 10 and y - 10 < cy < y + 10:
            matches.append((x,y))
   return(matches, draw)

def find_best_match(cx,cy,matches,w,h,draw):
   font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12, encoding="unic" )
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
      #print ("   Angles (img->cat), (cnt->img), (cnt->cat): ", img_cat_ang, img_cnt_ang, cat_cnt_ang, ang_diff1, ang_diff2, img_cat_dist)
      extra_match.append((mx,my,ang_diff1, img_cat_dist))

   if len(extra_match) > 0:
      sorted_extra =  sorted(extra_match,key=lambda x: x[2])
      for bx,by,bd,icd in sorted_extra:
         if bd < 30:
            break


      draw.text((bx+5,by), str(bd), font=font, fill=(255,255,255,128))
      draw.line((cx,cy, bx,by), fill=128)
      draw.text((cx+5,cy+5), str(icd), font=font, fill=(255,255,255,128))
      #draw.line((cx,cy, w/2,h/2), fill="blue")
      draw.ellipse((bx-6, by-6, bx+6, by+6),  outline ='red') 

      return(draw,bx,by)
   else :
      return(draw, 0, 0)


def find_fov_center (cal_file):
   #cal_file = "/mnt/ams2/cal/20180922105200-6.jpg"
   #catalog_filename = "/mnt/ams2/cal/20180922105200-6-indx.xyls"
   catalog_filename = cal_file.replace(".jpg", "-indx.xyls")
   #image_filename = "/mnt/ams2/cal/20180922105200-6.axy"
   image_filename = cal_file.replace(".jpg", ".axy")
   #plot_out_file = "/mnt/ams2/cal/20180922105200-6-mike-plot.jpg"
   plot_out_file = cal_file.replace(".jpg", "-center_plot.jpg")
   
   plot_image = Image.open(cal_file)
   draw = ImageDraw.Draw(plot_image)
   font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12, encoding="unic" )
   
   cat_points = dump_fits(catalog_filename)
   img_points = dump_fits(image_filename, image_filename)
   np.asarray(cat_points)
   np.asarray(img_points)
   w,h =  plot_image.size
   pc = 0
   lines = []
   for x,y in cat_points:
      if pc < 100:
         matches,draw = find_closest_match(x,y, img_points, w, h, draw)
         draw,sx,sy = find_best_match(x,y,matches,w,h, draw)
         if sx != 0:
            lines.append((sx,sy,x,y))
      pc = pc + 1
   draw.line((w/2,0, w/2,h), fill="white")
   draw.line((0,h/2, w,h/2), fill="white")
   all_med_x = []
   all_med_y = []
   for i in range(0, len(lines)-1):
      all_ixs = []
      all_iys = []
      for j in range(i+1, len(lines)-1):
         A = lines[i][0],lines[i][1]
         B = lines[i][2],lines[i][3]
         C = lines[j][0],lines[j][1]
         D = lines[j][2],lines[j][3]
         ix,iy = line_intersection((A,B),(C,D)) 
         all_ixs.append(ix)
         all_iys.append(iy)
   
      ix_median = np.median(all_ixs)
      iy_median = np.median(all_iys)
      if ix_median > 0:
         all_med_x.append(ix_median)
         all_med_y.append(iy_median)
   
   
   center_x = np.median(all_med_x)
   center_y = np.median(all_med_y)
   
   draw.ellipse((center_x-1, center_y-1, center_x+1, center_y+1),  outline ='yellow')
   
   for x,y in cat_points:
      draw.line((x,y, center_x, center_y), fill=128)
   
   plot_image.save(plot_out_file)
   print ("http://localhost" + plot_out_file)
   return(center_x, center_y, cat_points, img_points, w, h)

def find_dist_values(cal_file, center_x, center_y, cat_points, img_points):
  
   star_dict = {} 
   starlist = load_stars(cal_file)
   plot_image = Image.open(cal_file)
   plot_out_file = cal_file.replace(".jpg", "-distplot.png")
   plot_image = plot_image.convert("RGBA")
   w,h =  plot_image.size
   draw = ImageDraw.Draw(plot_image)
   font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12, encoding="unic" )
   used = []
   draw.ellipse((center_x-25, center_y-25, center_x+25, center_y+25),  outline =(255,255,255,0))
   for fact in range (1,11):
      draw.ellipse((center_x-(fact * 100), center_y-(fact*100), center_x+(fact*100), center_y+(fact*100)),  outline =(255,255,255,0))
   for x,y in cat_points:
      star_name = find_star_name(x,y,starlist)
      draw.text((x+5,y+5), star_name, font=font, fill=(255,255,255,255))
      matches = find_matching_star(x,y,img_points, center_x, center_y, used)
      matches =  sorted(matches,key=lambda x: x[2])
      #print ("MATCHES: ", matches)
      if len(matches) >= 1: 
         used.append(matches[0])
         mx = matches[0][0]
         my = matches[0][1]
         md = matches[0][2]
         mx = matches[0][0]
         my = matches[0][1]
         md = matches[0][2]
         star_dict[star_name] = {}   
         star_dict[star_name] = {'ix' : mx, 'iy' : my, 'cx': x, 'cy' : y, 'found' : 1 }   
         draw.ellipse((mx-5, my-5, mx+5, my+5),  outline ='red')
         draw.ellipse((x-5, y-5, x+5, y+5),  outline ='green')
         draw.line((x,y, mx,my), fill="white")
        
   #draw.line((center_x,0, center_x,h), fill="white")
   #draw.line((0,center_y, w,center_y), fill="white")
   draw.line((w/2,0, w/2,h), fill="white")
   draw.line((0,h/2, w,h/2), fill="white")

   grid_file = cal_file.replace(".jpg", "-grid.png")
   grid_image = Image.open(grid_file)
   grid_image = grid_image.convert("RGBA")


   star_data = []
   lines = []
   for star in star_dict:
      ix = star_dict[star]['ix']
      iy = star_dict[star]['iy']
      cx = star_dict[star]['cx']
      cy = star_dict[star]['cy']
      found = star_dict[star]['found']
      star_data.append((star,ix,iy,cx,cy))
      lines.append((ix,iy,cx,cy))
   new_center_x, new_center_y = find_new_center(lines)
   draw.ellipse((new_center_x-5, new_center_y-5, new_center_x+5, new_center_y+5),  outline =(0,0,255,255))

   

   #for x,y in cat_points:
   #   found = 0
   #   this_star_name = ""
   ##   for (star_name, ix,iy,cx,cy) in star_data:
   #      if int(float(cx)) == int(float(x)) and int(float(cy)) == int(float(y)):
   #         found = 1
   #         this_star_name = star_name
      #if found == 1:
      #   print("FOUND: ", this_star_name)
      #else:
      #   this_star_name = find_star_name(x,y,starlist)
      #   print("NOT FOUND: ", this_star_name)
      #   #draw.ellipse((x-7, y-7, x+7, y+7),  outline ="orange")

   alpha_blend = Image.blend(plot_image, grid_image, alpha=.2)
   alpha_blend.save(plot_out_file)
   star_dist_data = cal_file.replace(".jpg", "-star-dist-data.txt")
   fp = open(star_dist_data, "w")
   fp.write("star_dist_data=" + str(star_data))
   print("Star Data YO:", str(star_data))
   fp.close()

def find_matching_star(cx,cy, img_points, center_x, center_y,used):
   matches = []
   cat_center_dist = int(calc_dist(cx,cy,center_x,center_y))
   cat_center_ang = int(calc_angle((center_y, center_x),(cy,cx)))
   for x,y in img_points:
      if cat_center_dist > 400:
         if x -100 < cx < x + 100 and y - 100 < cy < y + 100:
            img_center_dist = int(calc_dist(center_x,center_y,x,y))
            img_cat_dist = int(calc_dist(cx,cy,x,y))
            img_center_ang = int(calc_angle((center_y,center_x),(y,x)))
            img_cat_ang = int(calc_angle((cy,cx),(y,x)))
            if cat_center_ang == img_center_ang :
               if img_center_dist < cat_center_dist:
                  dupe_status = check_dupe(x,y,used)
                  if dupe_status == 0:
                     matches.append((x,y,img_cat_dist))
      elif cat_center_dist < 400:
         if x -10 < cx < x + 10 and y - 10 < cy < y + 10:
            img_cat_dist = int(calc_dist(cx,cy,x,y))
            img_center_ang = int(calc_angle((center_y,center_x),(y,x)))
            img_cat_ang = int(calc_angle((cy,cx),(y,x)))
            if (cat_center_ang == img_center_ang) : 
#or (img_center_ang-1 < img_cat_ang < img_center_ang + 1):
               matches.append((x,y,img_cat_dist))
            #else:
            #   print ("INSPECT: ", cat_center_ang, img_center_ang, img_cat_ang )

   

   return(matches)

def find_new_center(lines):
   all_med_x = []
   all_med_y = []
   for i in range(0, len(lines)-1):
      all_ixs = []
      all_iys = []
      for j in range(i+1, len(lines)-1):
         A = lines[i][0],lines[i][1]
         B = lines[i][2],lines[i][3]
         C = lines[j][0],lines[j][1]
         D = lines[j][2],lines[j][3]
         ix,iy = line_intersection((A,B),(C,D))
         all_ixs.append(ix)
         all_iys.append(iy)

      ix_median = np.median(all_ixs)
      iy_median = np.median(all_iys)
      if ix_median > 0:
         all_med_x.append(ix_median)
         all_med_y.append(iy_median)


   center_x = np.median(all_med_x)
   center_y = np.median(all_med_y)

   return(center_x, center_y)

def check_dupe(x,y,used):
   dupe_status = 0 
   for ux,uy,uid in used:
      if ux == x and uy == y:
         dupe_status = 1 
   return(dupe_status)


def load_stars(cal_file):
   star_file = cal_file.replace(".jpg", "-stars.txt")
   sf = open(star_file, "r") 
   starlist = []
   for line in sf:
      line = line.replace("\n", "")
      line = line.replace(" Mike Star: ", "")
      data = line.split(" ") 
      if len(data) == 5:
         star_name = data[1]
         star_name = star_name.replace(" at ", "")
         star_img_x = data[3]
         star_img_x = star_img_x.replace("(", "")
         star_img_x = star_img_x.replace(",", "")
         star_img_y = data[4]
         star_img_y = star_img_y.replace(")", "")
         starlist.append((star_name, star_img_x, star_img_y))
   return(starlist)

def find_star_name(cx,cy,starlist):
   this_star_name = ""
   for star_name, x, y in starlist:
      if float(cx)-1 < float(x) < float(cx) + 1 and float(cy) -1 < float(y) < float(cy) + 1:
         this_star_name = star_name
         return(this_star_name)
   return(this_star_name)

cal_file = sys.argv[1]
fov_file = cal_file.replace(".jpg", "-fov-center.txt")
#cal_file = "/mnt/ams2/cal/20180922105200-6.jpg"
(center_x, center_y, cat_points, img_points,w,h) = find_fov_center(cal_file)
fov = open(fov_file, "w")
fov.write(str(center_x - (w/2)) + "," + str(center_y - (h/2)))
fov.close()
find_dist_values(cal_file, center_x, center_y, cat_points, img_points)


#!/usr/bin/python3

import subprocess
import datetime
import glob
import numpy as np
import cv2
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import sys
import os
import time 

import brightstardata as bsd
mybsd = bsd.brightstardata()
bright_stars = mybsd.bright_stars

def find_star_by_name(star_name):
   for bname, cons, ra, dec, mag in bright_stars:
      cons = cons.decode("utf-8")
      name = bname.decode("utf-8")
      if name == star_name:
         return(1,name, cons, ra,dec,mag)
   return(0,0,0,0,0,0)


def stop_solve():
   cmd = "killall astrometry-engine"
   os.system(cmd)
   #output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   cmd = "killall solve-field"
   os.system(cmd)
   #output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   #print (output)


def check_running(process_str):
   cmd = "ps -aux |grep " + process_str + " | grep -v grep | wc -l"
   print(cmd)
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   output = int(output.replace("\n", ""))
   print (output)
   return(int(output))


def cleanup(jpg_file,failed):

   # cleanup and move all extra files
   el = jpg_file.split("/")
   temp = el[-1]
   cal_dir = temp.replace(".jpg", "")
   if os.path.exists("/mnt/ams2/cal/solved/" + cal_dir):
      print ("already done.")
   else:
      os.mkdir("/mnt/ams2/cal/solved/" + cal_dir)
   if os.path.exists("/mnt/ams2/cal/failed/" + cal_dir):
      print ("already done.")
   else:
      os.mkdir("/mnt/ams2/cal/failed/" + cal_dir)
   if failed == 0:
      cmd = "mv /mnt/ams2/cal/" + cal_dir + "* /mnt/ams2/cal/solved/" + cal_dir + "/"
      print (cmd)
      os.system(cmd)
   else:
      cmd = "mv /mnt/ams2/cal/" + cal_dir + "* /mnt/ams2/cal/failed/" + cal_dir + "/"
      print (cmd)
      os.system(cmd)

def plot_bright_stars(jpg_file, image, star_data_file):
   bright_star_file = jpg_file.replace(".jpg", "-bright-stars.jpg")
   pil_image = Image.fromarray(image)
   draw = ImageDraw.Draw(pil_image)
   font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12, encoding="unic" )


   for data in star_data_file:
      (name, cons, ra, dec, mag, ast_x, ast_y) = data.split(",")
      ast_x = int(float(ast_x))
      ast_y = int(float(ast_y))
      draw.ellipse((ast_x-4, ast_y-4, ast_x+4, ast_y+4), )
      draw.text((int(float(ast_x)), int(float(ast_y) )), name, font = font, fill=(255,255,255))
      pil_image.save(bright_star_file)


def parse_astr_star_file(star_data_file):
   bright_stars_found = []
   fp = open(star_data_file, "r")
   for line in fp:
      fields = line.split(" ")
      #print (len(fields) )
      if len(fields) == 8:
         star_name = fields[4]
         ast_x = fields[6]
         ast_y = fields[7]
         ast_x = ast_x.replace("(", "")
         ast_x = ast_x.replace(",", "")
         ast_y = ast_y.replace(")", "")
         ast_y = ast_y.replace("\n", "")
      elif len(fields) == 9 :
         star_name = fields[5]
         star_name = star_name.replace("(", "")
         star_name = star_name.replace(")", "")
         ast_x = fields[7]
         ast_y = fields[8]
         ast_x = ast_x.replace("(", "")
         ast_x = ast_x.replace(",", "")
         ast_y = ast_y.replace(")", "")
         ast_y = ast_y.replace("\n", "")
         #print(star_name)
         (status, bname, cons, ra,dec,mag) = find_star_by_name(star_name)
         #print(status, bname, cons, ra,dec, mag)
         if int(status) == 1:
            data = bname + "," + cons + "," + str(ra) + "," + str(dec) + "," + str(mag) + "," + str(ast_x) + "," + str(ast_y)
            #print("Bright Star found:", bname, cons, ra,dec, mag, "Near position", ast_x, ast_y)
            bright_stars_found.append(data)

   for data in bright_stars_found :
      print(data)

   return(bright_stars_found)


def find_best_thresh(image, thresh_limit, type=0):
   go = 1
   while go == 1:
      _, thresh = cv2.threshold(image, thresh_limit, 255, cv2.THRESH_BINARY)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      if type == 0:
         cap = 50
      else:
         cap = 100
      if len(cnts) > cap:
         thresh_limit = thresh_limit + 1

      else:
         bad = 0
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])
            if w == image.shape[1]:
               bad = 1
            if type == 0 and (w >= 10 or h > 10):
               bad = 1
         if bad == 0:
            go = 0
         else:
            thresh_limit = thresh_limit + 1
   return(thresh_limit)


def block_mask(img, info):
   min_x,max_x,min_y,max_y = info
   img.setflags(write=1)
   img[min_y:max_y, min_x:max_x] = [0]
   return(img)

def find_flux(new_image, x,y,size,writeout=0):
   box = (x-size,y-size,x+size,y+size)

   flux_box = new_image.crop(box)
   flux_box = flux_box.resize((75,75), Image.ANTIALIAS)
   gray_flux_box = flux_box.convert('L')

   np_flux_box = np.asarray(gray_flux_box)
   np_flux_box = cv2.GaussianBlur(np_flux_box, (21, 21), 0)
   avg_flux = np.average(np_flux_box)
   max_flux = np.amax(np_flux_box)

   ffw= int(np_flux_box.shape[1] / 2)
   ffh = int(np_flux_box.shape[0] / 2)

   abr = 0
   for afx in range(0,np_flux_box.shape[1]):
      for afy in range(np_flux_box.shape[0]):
         pixel_val = np_flux_box[afx,afy]
         if pixel_val > abr:
            #print ("Brightest Pixel Value", afx, afy, pixel_val)
            brightest_pix = (afx,afy)
            abr = pixel_val

         if abr == 0:
            brightest_pix = (ffw,ffh)

         (cxx,cxy) = brightest_pix

         box_tiny = (cxx-1,cxy-1,cxx+1,cxy+1)
         np_flux_box_tiny = np_flux_box[cxy-1:cxy+1, cxx-1:cxx+1]
         total_flux = np.sum(np_flux_box_tiny)
    
         #cv2.rectangle(np_flux_box, (x,y), (x+2, y+2), (0,0,255),2)
         #np_flux_box.setflags(write=1)
         #print ("BRIGHTEST CENTER: ", cxy,cxx)
         #tag = str(x) + "," + str(y) + "/ " + str(cxx) + "," + str(cxy)
         #cv2.putText(np_flux_box, tag, (2, np_flux_box.shape[0] - 2), cv2.FONT_HERSHEY_SIMPLEX, .3, (255, 255, 255), 1)

         #cv2.circle(np_flux_box, (cxx,cxy), 10, (255,255,255), 1)
   print ("FLUX: ", avg_flux, max_flux, total_flux, x,y,cxx,cxy )
   return (int(avg_flux), int(max_flux), int(total_flux), cxx,cxy)



def find_stars(cal_file, show=0, extra_thresh = 0):
   if show == 1:
      cv2.namedWindow('pepe')
   print ("Starting on : ", cal_file)
   starlist_file = cal_file.replace(".jpg", "-pystarlist.txt")
   cal_image_cv = cv2.imread(cal_file)
   cal_image_pil = Image.fromarray(cal_image_cv)
   cal_img_width = int(cal_image_cv.shape[1])
   cal_img_height = int(cal_image_cv.shape[0])


   cal_image_cv = block_mask(cal_image_cv, (0,cal_img_width,cal_img_height-80,cal_img_height))
   cal_image_cv_gray = cv2.cvtColor(cal_image_cv, cv2.COLOR_BGR2GRAY)


   #print (cal_img_width, cal_img_height)

   avg_px = np.average(cal_image_cv_gray)
   max_pixel = np.amax(cal_image_cv_gray)
   #print ("AVG PX, BRIGHT PX", avg_px, max_pixel)

   lower_thresh = max_pixel - 10
   star_thresh = 10
   lower_thresh = avg_px * int(star_thresh)

   best_thresh = find_best_thresh(cal_image_cv_gray, 10, 0)
   best_thresh = best_thresh + extra_thresh 

   _, nice_threshold = cv2.threshold(cal_image_cv_gray, best_thresh, 255, cv2.THRESH_BINARY)
   (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   contours = len(cnts)
   cc = 0
   print("CNTS: ", contours)
   starlist = []
   if contours > 0 :
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         #print (x,y,w,h)
         x2 = x + w
         y2 = y + h
         px = x
         py = y
         #avg_flux, max_flux, total_flux, cx, cy = find_flux(cal_image_pil, int(px), int(py), 10,0)
         cv2.rectangle(cal_image_cv, (x,y), (x+w, y+h), (0,0,255),2)
         #starlist.append([x,y,w,h,avg_flux,max_flux,total_flux])
         starlist.append([x,y,w,h])
         cc = cc + 1


   # Display Image
   if show == 1:
      small_img = cv2.resize(cal_image_cv, (int(cal_img_width/2),int(cal_img_height/2)) )
      cv2.imshow('pepe', small_img)
      k = cv2.waitKey(3)
      #if k == 32:
      #   exit() 
   fpo = open(starlist_file, "w")
   fpo.write("starlist=" + str(starlist))
   fpo.close()
   return(starlist)

def batch_filter_bad(show = 0):
   files = glob.glob("/mnt/ams2/cal/*.jpg")   
   for cal_file in files:
      starlist = find_stars(cal_file, show, 5)
      if len(starlist) < 10:
         cmd = "mv " + cal_file + " /mnt/ams2/cal/bad/"
         os.system(cmd)

def batch_calibrate(show = 0):
   files = glob.glob("/mnt/ams2/cal/*.jpg")   
   for cal_file in files:
      starlist = find_stars(cal_file, show)
      print("Solving file")
      plate_solve(cal_file)

def plate_solve(cal_file):            

   cal_image_cv = cv2.imread(cal_file)
   cal_image_pil = Image.fromarray(cal_image_cv)
   width = int(cal_image_cv.shape[1])
   height = int(cal_image_cv.shape[0])

   wcs_file = cal_file.replace(".jpg", ".wcs")
   grid_file = cal_file.replace(".jpg", "-grid.png")
   star_file = cal_file.replace(".jpg", "-stars-out.jpg")
   star_data_file = cal_file.replace(".jpg", "-stars.txt")
   astr_out = cal_file.replace(".jpg", "-astrometry-output.txt")
   wcs_info_file = cal_file.replace(".jpg", "-wcsinfo.txt")
   quarter_file = cal_file.replace(".jpg", "-1.jpg")

  
   print("/usr/local/astrometry/bin/solve-field " + cal_file + " --verbose --no-delete-temp --overwrite --width=" + str(width) + " --height=" + str(height) + " --scale-low 10 --scale-high 80 > " + astr_out)
   os.system("/usr/local/astrometry/bin/solve-field " + cal_file + " --verbose --no-delete-temp --overwrite --width=" + str(width) + " --height=" + str(height) + " --scale-low 40 --scale-high 80 > " + astr_out + " & ")

   running = 1
   start_time = datetime.datetime.now()
   failed = 0 
   while running >= 1:
      running = check_running("solve-field")
      print ("RUNNING: ", running)
      cur_time = datetime.datetime.now()
      td = (cur_time - start_time).total_seconds() 
      print ("TIMES:", td )
      time.sleep(10) 
      if int(td) > 120:
         print("KILL ASTROMETRY PROCESS...", td)
         stop_solve()
         failed = 1
      #   exit()
      
   if failed == 0:
      os.system("grep Mike " + astr_out + " >" +star_data_file)

      cmd = "/usr/bin/jpegtopnm " + cal_file + "|/usr/local/astrometry/bin/plot-constellations -w " + wcs_file + " -o " + grid_file + " -i - -N -C -G 600"
      print (cmd)
      os.system(cmd)

      cmd = "/usr/local/astrometry/bin/wcsinfo " + wcs_file + " > " + wcs_info_file
      os.system(cmd)

      bright_star_data = parse_astr_star_file(star_data_file)
      plot_bright_stars(cal_file, cal_image_cv, bright_star_data)

      cmd = "./calibrate_image_step2.py " + cal_file
      os.system(cmd)

      #cmd = "./fisheye-test.py " + cal_file
      #os.system(cmd)

   cleanup(cal_file, failed)


cal_file = sys.argv[1]
show = 0
if len(sys.argv) > 2:
   show = 1
if cal_file == "batch":
   batch_filter_bad(show)
elif cal_file == "batch_cal":
   batch_calibrate(show)
else:
   stars = find_stars(cal_file)




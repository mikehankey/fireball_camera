#!/usr/bin/python3

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


class MFTCalibration:
   def __init__(self):
      print ("Calibration Class") 
      # Q: What do we want to do with this class? 
      # A: 1) Pass it an image and get accurate x,y,flux points for stars in the image 
      #    2) Use those x,y,flux points to create a star drawing  
      #    3) Pass that star drawing to astometry.net 
      #    4) Will produce and maintain the following images and data items
      #    5) Original copy of the image
      #    6) Annotated copy of the image showing star positions
      #    7) RA/DEC Plotted version of the image
      #    8) WCS enabled viewing 
      #    9) List of star objects and info
      self.starlist = [] # x,y,f,name
      self.block_masks = []
      self.image = None
      self.marked_image = None
      self.star_drawing = None
      self.annotated_image = None
      self.path = None
      self.wcs_file = None
      self.star_data_file = None
      self.constellation_file = None
 

   def update_path(self, path):
      self.path = path 

   def update_block_masks(self, block_masks):
      self.block_masks = block_masks 

   def update_starlist(self, starlist):
      self.starlist = starlist

   def update_image(self, image):
      self.image = image
      print("calibration image updated.")

   def update_marked_image(self, image):
      self.marked_image = image

   def update_star_drawing(self, image):
      self.star_drawing = image

   def find_radec_from_xy (self, x, y):
      cmd = "/usr/local/astrometry/bin/wcs-xy2rd -w " + self.wcs_file + " -x " + str(x) + " -y " + str(y)
      output = subprocess.check_output(cmd, shell=True)
      (t, radec) = output.decode("utf-8").split("RA,Dec")
      radec = radec.replace('(', '')
      radec = radec.replace(')', '')
      radec = radec.replace('\n', '')
      radec = radec.replace(' ', '')
      ra, dec = radec.split(",")
      print ("ASTR RA/DEC: ", ra,dec)
      radd = float(ra)
      decdd = float(dec)
      ra= self.RAdeg2HMS(ra)
      #(h,m,s) = ra.split(":")
      #ra = h + " h " + m + " min"
      dec = self.Decdeg2DMS(dec)
      return(ra, dec, radd, decdd)

   def Decdeg2DMS(self, Decin ):
      Decin = float(Decin)
      if(Decin<0):
         sign = -1
         dec  = -Decin
      else:
         sign = 1
         dec  = Decin

      d = int( dec )
      dec -= d
      dec *= 100.
      m = int( dec*3./5. )
      dec -= m*5./3.
      s = dec*180./5.

      if(sign == -1):
         out = '-%02d:%02d:%06.3f'%(d,m,s)
      else: 
         out = '+%02d:%02d:%06.3f'%(d,m,s)
      return out

   def RAdeg2HMS(self, RAin ):
      RAin = float(RAin)
      if(RAin<0):
         sign = -1
         ra   = -RAin
      else:
         sign = 1
         ra   = RAin

      h = int( ra/15. )
      ra -= h*15.
      m = int( ra*4.)
      ra -= m/4.
      s = ra*240.

      if(sign == -1):
         out = '-%02d:%02d:%06.3f'%(h,m,s)
      else: 
         out = '+%02d:%02d:%06.3f'%(h,m,s)

      return out


   def find_flux(self, x,y,size):
      box = (x-size,y-size,x+size,y+size)

      flux_box = self.new_image.crop(box)
      gray_flux_box = flux_box.convert('L')

      np_flux_box = np.asarray(gray_flux_box)
      #np_flux_box = cv2.GaussianBlur(np_flux_box, (21, 21), 0)
      avg_flux = np.average(np_flux_box)
      max_flux = np.amax(np_flux_box)

      return (int(avg_flux), int(max_flux))

   def find_stars(self):
      self.new_image = self.image
      print ("Finding stars...")
      if self.new_image == None:
         print ("sorry no image!")
         return()
      gray_new_image = self.new_image.convert('L')
      np_color_image = np.asarray(self.new_image)
      np_new_image = np.asarray(gray_new_image)
      np_new_image.setflags(write=1)
      # apply masks
      np_new_image[340:360, 0:230] = [0]

      avg_px = np.average(np_new_image)
      ax_pixel = np.amax(np_new_image)
      #print ("AVG PX, BRIGHT PX", avg_px, ax_pixel)

      lower_thresh = ax_pixel - 10

      lower_thresh = avg_px * 3

      #np_new_image = cv2.GaussianBlur(np_new_image, (1, 1), 0)
      _, nice_threshold = cv2.threshold(np_new_image, lower_thresh, 255, cv2.THRESH_BINARY)
      (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      contours = len(cnts)
      x,y,w,h = 0,0,0,0
      starlist_value = ""
      self.star_image = self.new_image
      draw = ImageDraw.Draw(self.star_image)
      if contours > 0:
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])
            print (x,y,w,h)
            x2 = x + w
            y2 = y + h
            px = int(x + (w/2))
            py = int(y + (h/2))
            avg_flux, max_flux = self.find_flux(int(px), int(py), 10)
            cv2.rectangle(np_color_image, (x,y), (x+w, y+h), (0,0,255),2)
            starlist_txt = str(px) + "," + str(py)
            #self.starlist_value = Label(self.master, text=starlist_txt  )
            #self.starlist_value.grid(row=7+i, column=0)
            #self.starlist_value.extra="starlist"
            draw.point((px, py), 'red')
            self.starlist.append([x,y,w,h,avg_flux,max_flux])
      self.marked_image = Image.fromarray(np_color_image)
      print(self.starlist)
      #self.displayImage(self.star_image)

   def solve_field(self):
      dataxy = self.path.replace(".jpg", "-xy.txt")
      fitsxy = self.path.replace(".jpg", ".xy")
      star_drawing_fn = self.path.replace(".jpg", "-sd.jpg")
      self.wcs_file = self.path.replace(".jpg", "-sd.wcs")
      self.constellation_file = self.path.replace(".jpg", "-sd-grid.png")
      self.star_data_file = self.path.replace(".jpg", "-sd-stardata.txt")


      axy = self.path.replace(".jpg", ".axy")
      fp = open(dataxy, "w")
      fp.write("x,y\n")
 

      self.star_drawing = Image.new('L', (640,360))
      draw = ImageDraw.Draw(self.star_drawing)

      for star in self.starlist:
         x,y,h,w,af,mf  = star
         x1 = int(x)-2
         y1 = int(y)-2
         x2 = int(x)+2
         y2 = int(y)+2
         draw.ellipse((x1, y1, x2, y2), fill=255)
         avg_flux, max_flux = self.find_flux(int(x), int(y), 10)
         fits_data = str(x) + "," + str(y) + "," + str(avg_flux) + "," + str(max_flux) + "\n"
         fp.write(fits_data)
      fp.close()
      self.star_drawing.save(star_drawing_fn)

      cmd = "/usr/local/astrometry/bin/solve-field " + star_drawing_fn + " --overwrite --width=640 --height=360 --scale-units degwidth --scale-low 60 --scale-high 85 --no-remove-lines"
      print (cmd)
      os.system(cmd)

      # This one WORKS!
      #cmd = "/usr/bin/jpegtopnm " + self.path + "|/usr/local/astrometry/bin/plot-constellations -w " + self.wcs_file + " -o " + self.constellation_file + " -i - -N -C -G 600"
      #cmd = "/usr/bin/jpegtopnm " + self.path + "|/usr/local/astrometry/bin/plot-constellations -w " + self.wcs_file + " -o " + self.constellation_file + " -i - -N -B -b 60 -G 600"
      cmd = "/usr/bin/jpegtopnm " + self.path + "|/usr/local/astrometry/bin/plot-constellations -w " + self.wcs_file + " -o " + self.constellation_file + " -i - -C -B -b 200 -v -f 0 -G 600"

      print (cmd)
      os.system(cmd)

      cmd = "/usr/local/astrometry/bin/wcsinfo " + self.wcs_file + " > " + self.star_data_file
      os.system(cmd)

      #self.astr_path = self.path.replace(".jpg", "-sd-objs.png")
      self.np_annotated_image = cv2.imread(self.constellation_file)
      self.annotated_image = Image.fromarray(self.np_annotated_image)


#!/usr/bin/python3
import re
import fitsio
import sys

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
      self.man_sources = [] # x
      self.block_masks = []
      self.image = None
      self.new_image = None
      self.marked_image = None
      self.star_drawing = None
      self.annotated_image = None
      self.path = None
      self.path_corr = None
      self.path_solve_field_output = None
      self.wcs_file = None
      self.star_data_file = None
      self.constellation_file = None

      self.debug = 0
      self.star_thresh = None
      self.odds_to_solve = None
      self.code_tolerance = None

      #self.matching_stars = []
      self.matching_stars = []
      self.my_stars = []
      self.found_stars = []
      self.not_found_stars = []
      self.named_stars = []
      #exec(open("brightstarsdata.py").read())
      import brightstardata as bsd
      mybsd = bsd.brightstardata()
      self.bright_stars = mybsd.bright_stars
 
      #ALTAZ 
      self.loc_lat = None
      self.loc_lon = None
      self.loc_alt = None
      self.cal_time = None
      self.location = None

   def load_solution():
      # Actual Images 
      # detected_stars -- marked up image (show all detections, found in catalog, used in solution, mapped to x,y)
      # starmap -- astrometry.net star map
      # original image
      # lens distortion image

      # Image file names
 
      # lists, values, totals and status

      # AZ Information
      # astropy objects Earthlocation

   def parse_file_date(self, full_file_name):
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


   def make_star_plot(self):
      print ("Make star plot.")
      image_file = self.path.replace(".jpg", "-sd.new")
      plot_file = self.path.replace(".jpg", "-sd-starplot.png")

      hdu = fits.open(image_file)
      hdu.info()

      wcs = WCS(hdu[0].header)

      fig = plt.figure(figsize=(10,6.5), dpi = 80)

      ax = fig.add_axes([0.0,0.0,.8,.8],projection=wcs)
      ax.set_xlim(-0.1, hdu[0].data.shape[1] - 0.1)
      ax.set_ylim(-0.1, hdu[0].data.shape[0] - 0.1)
      ax.invert_yaxis()
      ax.imshow(hdu[0].data, origin='lower', shape = (640,360))

      overlay = ax.get_coords_overlay('fk5')

      overlay['ra'].set_ticks(color='white', number=8)
      overlay['dec'].set_ticks(color='white', number=8)

      overlay['ra'].set_axislabel('Right Ascension')
      overlay['dec'].set_axislabel('Declination')
      overlay.grid(color='white', linestyle='dashed', alpha=0.5)

      plt.savefig(plot_file)
      os.system("convert " + plot_file + " -flip testf.png")
      os.system("convert testf.png -flip " + plot_file )
      plt.close('all')

   def load_found_stars(self):
      self.my_stars = []
      h = fitsio.read_header(self.path_corr, ext=1)
      n_entries = h["NAXIS2"]
      fits = fitsio.FITS(self.path_corr, iter_row_buffer=1000)
      for i in range(n_entries):
         my_x = fits[1][i][0][0]
         my_y = fits[1][i][0][1]
         self.my_stars.append((my_x, my_y))

   def find_closest_star_in_catalog(self,x,y,myra,mydec,factor):
      matches = []
      raran = range(int(float(myra)-factor), int(float(myra)+factor))
      decran = range(int(float(mydec)-factor), int(float(mydec)+factor))
      for bname, cons, ra, dec, mag in self.bright_stars:
         cons = cons.decode("utf-8") 
         name = bname.decode("utf-8")
         #print (name, cons)
         if int(float(ra)) in raran and int(float(dec)) in decran and float(mag) < 10:
            print ("Possible match: ", name, x,y, myra, mydec, ra,dec,mag)
            matches.append((str(name), str(cons), x,y, myra, mydec,float(ra), float(dec), float(mag)))
         else :
            if self.debug == 1:
               print ("No stars close to: ", myra,mydec,ra,dec)
            no = 1
      if len(matches) == 0:
         matches.append((0,0,x,y,myra,mydec,0,0,0))
         print ("COULD NOT FIND STAR IN CATALOG WITH:", x,y,myra,mydec,factor)
      else:
         print (len(matches), " matches found") 
      return(matches)

   def name_stars(self):
      self.found_stars = []
      self.not_found_stars = []
      self.named_stars = []
      finds = 0
      self.load_found_stars()
      for (x,y) in self.my_stars:
         (ra,dec,radd,decdd) = self.find_radec_from_xy(x,y)
         matches = self.find_closest_star_in_catalog(x,y,radd,decdd,1)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,2)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,4)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,5)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,6)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,7)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,8)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,9)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,10)

         if matches[0][0] != 0:
            finds = finds + 1

         # choose brightest if more than 1 match returns
         bright = 10
         best_match = []
         if len(matches) > 1:
            for (name, cons, x,y, myra, mydec,ra, dec, mag) in matches[:]:
               if float(mag) < bright:
                  bright = mag
                  best_matches = [(name, cons, x,y, myra, mydec,ra, dec, mag)]
            matches = best_matches
            (name, cons, x,y, myra, mydec,ra, dec, mag) = matches[0]
         else:
            print(matches[0])
            (name, cons, x,y, myra, mydec,ra, dec, mag) = matches[0]
         print("NAME:", str(name))
         if str(name) != '':
            self.found_stars.append((str(name), str(cons), x,y, myra, mydec,ra, dec, mag))
         else:
            print("NO NAME FOUND:", str(name), x,y)
            self.not_found_stars.append ((str(name) , str(cons), x , y , 0, 0, myra , mydec , 0, 0, 0))
        

      header = "name,lx,ly,cx,cy,lra,ldec,ra,dec,mag"
      print (header)
      for (name, cons, x,y, myra, mydec,ra, dec, mag) in self.found_stars:
         name = str(name)
         if name == "":
            name = "noname"
            print ("No Name on list!")
         else: 
            cor_x, cor_y = self.find_star_match(name, cons)
            self.named_stars.append ((str(name) , str(cons), x , y , cor_x , cor_y , myra , mydec , ra , dec , mag))

      print ("Total Stars = ", len(self.my_stars))
      print ("Total Found in Catalog = ", len(self.found_stars))
      print ("Total Named Stars with x,y & correct x,y = ", len(self.named_stars))
      print ("Total Not Found = ", len(self.not_found_stars))

 
   def find_star_match(self, name, cons):
      file = open(self.path_solve_field_output)
      name = str(name.replace(" ", ""))
      cons = str(cons.replace(" ", ""))
      for line in file:
         if "Mike" in line:
            line = line.replace("\n", "")
            (a,b) = line.split(":")
            try:
               mname, coords = b.split(" at ")
            except:
               print("Can't parse this line", line)
               exit()
            tr1, tr2 = coords.split(")")
            tr1 = tr1.replace("(", "")
            tr1 = tr1.replace(" ", "")
            cx,cy = tr1.split(",")
            if "(" in mname:
               mname,tr3 = mname.split("(")
            mname = str(mname.replace(" ", ""))
            name = str(name.replace(" ", ""))
            if "(" in mname:
               print (name, line)
               (tr, mname) = mname.split("(")
               (mname, tr) = mname.split(")")
               mname = str(mname.replace(" ", ""))

            if str(mname) == str(name) or str(mname) == str(cons):
               print ("Found: ", name, mname)
               return(cx,cy)
      print ("Not Found: ", name, cons, mname)
      return(0,0)
 


 

   def update_path(self, path):
      self.path = path 
      self.path_corr = path.replace(".jpg", "-sd.corr")
      self.path_solve_field_output = path.replace(".jpg", "-solve-field.txt")

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

   def find_radec_from_xy_pya(self, x,y):

      image_file = self.path.replace(".jpg", "-sd.new")
      W = WCS(image_file)
      self.target = SkyCoord.from_pixel(x,y,W)
      ra = self.target.ra
      dec = self.target.dec
      print(ra,dec)
      return(ra,dec,ra,dec)

   def find_radec_from_xy (self, x, y):
      cmd = "/usr/local/astrometry/bin/wcs-xy2rd -w " + self.wcs_file + " -x " + str(x) + " -y " + str(y)
      output = subprocess.check_output(cmd, shell=True)
      (t, radec) = output.decode("utf-8").split("RA,Dec")
      radec = radec.replace('(', '')
      radec = radec.replace(')', '')
      radec = radec.replace('\n', '')
      radec = radec.replace(' ', '')
      ra, dec = radec.split(",")
      #print ("ASTR RA/DEC: ", ra,dec)
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
      flux_box = flux_box.resize((75,75), Image.ANTIALIAS)
      gray_flux_box = flux_box.convert('L')

      np_flux_box = np.asarray(gray_flux_box)
      np_flux_box = cv2.GaussianBlur(np_flux_box, (21, 21), 0)
      avg_flux = np.average(np_flux_box)
      max_flux = np.amax(np_flux_box)
      #cv2.imwrite("/var/www/html/out/cal/crop" + str(int(max_flux)) + ".jpg", np_flux_box) 
      return (int(avg_flux), int(max_flux))

   def add_to_starlist(self, x,y,w,h):
      if self.new_image is None:
         self.new_image = self.image
      print (x,y,w,h)
      x2 = x + w
      y2 = y + h
      px = int(x + (w/2))
      py = int(y + (h/2))
      avg_flux, max_flux = self.find_flux(int(px), int(py), 10)
      self.starlist.append([x,y,w,h,avg_flux,max_flux])
      for source in self.starlist:
         print ("starlist is")
         print (source)

   def del_from_starlist(self, mx,my):

      xran = range(mx-3, mx+3)
      yran = range(my-10, my+10)
      ok_to_add = 1
      c = 0
      for source in self.starlist[:]:
         tx,ty,w,h,a,m = source
         if tx in xran and ty in yran:
             print ("This source exists, lets remove it!")
             #del self.starlist[c]
             self.starlist.remove(source)
      c = c + 1
      for source in self.starlist:
         print ("starlist is")
         print (source)


      



   def find_stars(self):
      self.starlist = []
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
      np_new_image[320:360, 0:640] = [0]
      img_width = int(np_new_image.shape[1])
      img_height = int(np_new_image.shape[0])
      print ("IM WH:", img_width, img_height)
      for x,y in self.block_masks:
         min_x = x - 10
         max_x = x + 10
         min_y = y - 10
         max_y = y + 10
         #print ("Mask around : ", min_x,max_x,min_y,max_y)
         np_new_image.setflags(write=1)
         np_new_image[min_y:max_y, min_x:max_x] = [0]


      avg_px = np.average(np_new_image)
      ax_pixel = np.amax(np_new_image)
      #print ("AVG PX, BRIGHT PX", avg_px, ax_pixel)

      lower_thresh = ax_pixel - 10

      lower_thresh = avg_px * int(self.star_thresh) 

      #np_new_image = cv2.GaussianBlur(np_new_image, (1, 1), 0)
      _, nice_threshold = cv2.threshold(np_new_image, lower_thresh, 255, cv2.THRESH_BINARY)
      (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      contours = len(cnts)
      x,y,w,h = 0,0,0,0
      starlist_value = ""
      self.star_image = self.new_image
      draw = ImageDraw.Draw(self.star_image)
      cc = 0
      if contours > 0 :
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])

            if (x > img_width):
               print ("WTFX:", x)
            if (y > img_width):
               print ("WTFY:", y)


            #print (x,y,w,h)
            x2 = x + w
            y2 = y + h
            px = int(x + (w/2))
            py = int(y + (h/2))
            avg_flux, max_flux = self.find_flux(int(px), int(py), 10)
            if avg_flux > 0:
               ff = max_flux / avg_flux
            else:
               avg_flux = 1
            if max_flux > 30 and (w < 6 and h < 6) and ff > 2.5:
               cv2.rectangle(np_color_image, (x,y), (x+w, y+h), (0,0,255),2)
               starlist_txt = str(px) + "," + str(py)
               self.starlist.append([x,y,w,h,avg_flux,max_flux])
            cc = cc + 1
      self.marked_image = Image.fromarray(np_color_image)
      #print(self.starlist)
      #self.displayImage(self.star_image)


   def solve_field(self):
      print ("LAT/LON", self.loc_lat, self.loc_lon)
      #self.location = EarthLocation.from_geodetic(float(self.loc_lat)*u.deg,float(self.loc_lon)*u.deg,float(self.loc_alt)*u.m)
      self.location = EarthLocation.from_geodetic(float(self.loc_lon)*u.deg,float(self.loc_lat)*u.deg,float(self.loc_alt)*u.m)
      print ("solving field.")
      clean_path = self.path.replace(".jpg", "-sd*")
      cmd = "rm " + str(clean_path)
      print(cmd)
      os.system(cmd)
      clean_sol = self.path.replace(".jpg", "-solve-field.txt")
      cmd = "rm " + str(clean_sol)
      print(cmd)
      os.system(cmd)
      #exit()
      dataxy = self.path.replace(".jpg", "-xy.txt")
      fitsxy = self.path.replace(".jpg", ".xy")
      star_drawing_fn = self.path.replace(".jpg", "-sd.jpg")
      solve_out = self.path.replace(".jpg", "-solve-field.txt")
      self.wcs_file = self.path.replace(".jpg", "-sd.wcs")
      self.constellation_file = self.path.replace(".jpg", "-sd-grid.png")
      self.star_data_file = self.path.replace(".jpg", "-sd-stardata.txt")
      self.solved_file = self.path.replace(".jpg", "-sd.solved")
      self.az_out_file = self.path.replace(".jpg", "-altaz.txt")


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
      print("Saving star drawing here: ", star_drawing_fn) 
      self.star_drawing.save(star_drawing_fn)

      cmd = "/usr/local/astrometry/bin/solve-field " + star_drawing_fn + " --overwrite --width=640 --height=360 --scale-units degwidth --scale-low 60 --scale-high 85 --no-remove-lines -cpulimit=15 --odds-to-solve " + str(self.odds_to_solve) + " --code-tolerance " + str(self.code_tolerance) + " 2>&1 > " + solve_out
      print (cmd)
      os.system(cmd)

      if os.path.isfile(self.solved_file):
         print ("solve success! :)")
         self.solve_success = 1
      else:
         print ("solve failed :(")
         self.solve_success = 0
         self.np_annotated_image = cv2.imread(self.path)
         self.annotated_image = Image.fromarray(self.np_annotated_image)

      if self.solve_success == 1:
         cmd = "/usr/bin/jpegtopnm " + self.path + "|/usr/local/astrometry/bin/plot-constellations -w " + self.wcs_file + " -o " + self.constellation_file + " -i - -C -B -b 500 -v -f 0 -G 600 2>&1 >> " + solve_out

         print (cmd)
         os.system(cmd)

         cmd = "/usr/local/astrometry/bin/wcsinfo " + self.wcs_file + " > " + self.star_data_file
         os.system(cmd)

         self.np_annotated_image = cv2.imread(self.constellation_file)
         self.annotated_image = Image.fromarray(self.np_annotated_image)
         self.name_stars()
         #for (name, x,y, myra, mydec,ra, dec, mag) in self.found_stars:
         #self.make_star_plot()

         # ALT AZ
         (alt,az) = self.convert_xy_to_altaz(320,180)
         print ("CENTER ALTAZ:", alt, az)
         data = "CENTER,320,180," + str(az) + "," + str(alt) + "\n"
         if alt < 10:
            self.solve_success = 0

         (alt,az) = self.convert_xy_to_altaz(0,0)
         print ("TL ALTAZ:", alt, az)
         data = data + "TL,0,0," + str(az) + "," + str(alt) + "\n"

         (alt,az) = self.convert_xy_to_altaz(640,0)
         print ("TR ALTAZ:", alt, az)
         data = data + "TR,640,0," + str(az) + "," + str(alt) + "\n"

         (alt,az) = self.convert_xy_to_altaz(0,360)
         print ("BL ALTAZ:", alt, az)
         data = data + "BL,0,360," + str(az) + "," + str(alt) + "\n"

         (alt,az) = self.convert_xy_to_altaz(640,360)
         print ("BR ALTAZ:", alt, az)
         data = data + "BR,640,360," + str(az) + "," + str(alt) + "\n"
         azout = open(self.az_out_file, "w")
         azout.write(data)
         azout.close() 
         #self.draw_az_grid()

   def draw_az_grid(self):
      first_list = []
      az_grid = self.new_image
      az_grid_gray = az_grid.convert('L')
      az_grid_np = np.asarray(az_grid_gray)
      for y in range(az_grid_np.shape[0]):
         if (y % 100 == 0) :
            for x in range(az_grid_np.shape[1]):
               if (x % 100 == 0) :
                  (alt,az) = self.convert_xy_to_altaz(x,y)
                  print (x,y,alt,az)
                  first_list.append((x,y,alt,az))
      for points in first_list:
         print (points)


   def convert_xy_to_altaz(self, x,y):
      (ra, dec, radd, decdd) = self.find_radec_from_xy_pya(x, y)
      radd = self.convert_dms_to_ddms(radd)
      decdd = self.convert_dms_to_ddms(decdd)
      #print ("TARGET: ", radd, decdd)
      self.target = SkyCoord(ra=radd*u.degree, dec=decdd*u.degree, frame='icrs')
      altaz = self.target.transform_to(AltAz(location=self.location, obstime=Time(self.cal_time)))
      alt = self.convert_dms_to_ddms(str(altaz.alt))
      az = self.convert_dms_to_ddms(str(altaz.az))
      return(alt,az)

   def convert_dms_to_ddms(self, dms):
         temp = str(dms)
         d,m,s,x = re.split("d|m|s", temp)
         s = float(s)/60
         m = (int(m)/60) + s
         d = int(d) + float(m)
         return(d)

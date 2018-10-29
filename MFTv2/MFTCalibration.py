#!/usr/bin/python3
import re
import fitsio
import sys
from PIL import ImageFont
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
      self.solve_success = 0
      self.padding = 0

      self.debug = 0
      self.star_thresh = None
      self.odds_to_solve = None
      self.code_tolerance = None
      self.image_width = None
      self.image_height = None

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

   def find_best_thresh(self, image, thresh_limit):
      go = 1
      while go == 1:
         _, thresh = cv2.threshold(image, thresh_limit, 255, cv2.THRESH_BINARY)
         (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         if len(cnts) > 50:
            thresh_limit = thresh_limit + 2
         else:
            go = 0
         print ("BEST THRESH:", thresh_limit)
      return(thresh_limit)


   def save_solution(self):
      #image, new_image, marked_image, star_drawing, annotated_image 
      solution_file = self.path.replace(".jpg", "-solution.txt")
      sf = open(solution_file, "w")
      sf.write("path=\""+ str(self.path) + "\"\n")
      sf.write("path_corr=\""+ str(self.path_corr) + "\"\n")
      sf.write("path_solve_field_output=\""+ str(self.path_solve_field_output) + "\"\n")
      sf.write("wcs_file=\""+ str(self.wcs_file) + "\"\n")
      sf.write("star_data_file=\""+ str(self.star_data_file) + "\"\n")
      sf.write("constellation_file=\""+ str(self.constellation_file) + "\"\n")

      sf.write("loc_lat="+ str(self.loc_lat) + "\n")
      sf.write("loc_lon="+ str(self.loc_lon) + "\n")
      sf.write("loc_alt="+ str(self.loc_alt) + "\n")
      sf.write("cal_time=\""+ str(self.cal_time) + "\"\n")
      sf.write("star_thresh="+ str(self.star_thresh) + "\n")
      sf.write("odds_to_solve="+ str(self.odds_to_solve) + "\n")
      sf.write("code_tolerance="+ str(self.code_tolerance) + "\n")
      sf.write("az_center="+ str(self.az_center) + "\n")
      sf.write("alt_center="+ str(self.alt_center) + "\n")

      sf.write("image_width=" + str(self.image_width) + "\n")
      sf.write("image_height=" + str(self.image_height) + "\n")

      sf.write("block_masks="+ str(self.block_masks) + "\n")

      sf.write("my_stars="+ str(self.my_stars) + "\n")
      sf.write("starlist="+ str(self.starlist) + "\n")
      sf.write("man_sources="+ str(self.man_sources) + "\n")
      sf.write("not_found_stars="+ str(self.not_found_stars) + "\n")
      sf.write("found_stars="+ str(self.found_stars) + "\n")
      sf.write("matching_stars="+ str(self.matching_stars) + "\n")
      sf.write("named_stars="+ str(self.named_stars) + "\n")
      sf.write("azinfo="+ str(self.azinfo) + "\n")
      
      sf.close() 

   def load_solution(self):

      solution_file = self.path.replace(".jpg", "-solution.txt")
      print ("Loading", solution_file)
      sf = open(solution_file, "r")
      for lines in sf:
         line, jk = lines.split("\n")
         field, val = line.split("=")
         print (field, val) 

         exec("self."+line)
      
      # Actual Images 
      print ("opening cons:", self.constellation_file)
      self.solve_success = 1
      self.star_id_image_file = self.path.replace(".jpg", "-starid.jpg")

      self.star_id_image = cv2.imread(self.star_id_image_file)
      self.star_id_image = Image.fromarray(self.star_id_image)

      self.np_annotated_image = cv2.imread(self.constellation_file)
      self.annotated_image = Image.fromarray(self.np_annotated_image)
      
      star_drawing_fn = self.path.replace(".jpg", "-sd.jpg")
      self.np_star_drawing = cv2.imread(star_drawing_fn)
      self.star_drawing = Image.fromarray(self.np_star_drawing)

     
      # detected_stars -- marked up image (show all detections, found in catalog, used in solution, mapped to x,y)
      # starmap -- astrometry.net star map
      # original image
      # lens distortion image

      # Image file names
      if len(self.path) > 0:
         self.image = cv2.imread(self.path)
         self.image = Image.fromarray(self.image)
         self.new_image = self.image
 
      # lists, values, totals and status

      # AZ Information
      # astropy objects Earthlocation
      self.location = EarthLocation.from_geodetic(float(self.loc_lon)*u.deg,float(self.loc_lat)*u.deg,float(self.loc_alt)*u.m)
      self.update_star_id_image()




   def update_star_id_image(self):
      name_star_data_file = self.path.replace(".jpg", "-named_star_data.txt")
      star_id_image_file = self.path.replace(".jpg", "-starid.jpg")
      fp = open (name_star_data_file, "w")
      print ("STARID IMAGE FILE:", star_id_image_file)
      if self.image is None:
         print ("Self.image is NONE!")
      self.star_id_image = self.image
      found_points = []
      star_id_image_np = np.asarray(self.star_id_image)
      for (name, cons, x,y, cx, cy, myra, mydec,ra, dec, mag,diffra,diffdec) in self.named_stars:
         x = int(float(x))
         y = int(float(y))
         cx = int(float(cx))
         cy = int(float(cy))
         cv2.circle(star_id_image_np, (x,y), 3, (255,255,255), 1)
         cv2.circle(star_id_image_np, (cx,cy), 4, (0,255,0), 1)
         named_star_data =  str(name) + "," + str(cons) + "," + str(x) + "," + str(y) + "," + str(cx) + "," + str(cy) + "," + str(myra) + "," + str(mydec) + "," + str(ra) + "," + str(dec) + "," + str(mag) + ","
         fp.write(named_star_data + "\n")
         found_points.append((x,y))
      print ("Not found list is: ", len(self.not_found_stars))
      for (name, cons, x,y, cx, cy, myra, mydec,ra, dec, mag) in self.not_found_stars:
         named_star_data =  str(name) + "," + str(cons) + "," + str(x) + "," + str(y) + "," + str(cx) + "," + str(cy) + "," + str(myra) + "," + str(mydec) + "," + str(ra) + "," + str(dec) + "," + str(mag) + ","
         fp.write(named_star_data + "\n")
         print("Not found list: ", x,y, myra, mydec)
         x = int(float(x))
         y = int(float(y))
         cv2.circle(star_id_image_np, (x,y), 2, (255,0,0), 1)

      fp.close()
      self.star_id_image = Image.fromarray(star_id_image_np)
      draw = ImageDraw.Draw(self.star_id_image)
      font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12, encoding="unic" )

      avg_star_xy = np.average(found_points, axis = 0)
      print ("AVG XY OF STAR FIELD: ", avg_star_xy)
      draw.text((avg_star_xy[0], avg_star_xy[1]), "X", font = font, fill=(255,255,255))
      draw.text((avg_star_xy[0]+15, avg_star_xy[1]), "Plate Center X,Y:" + str(int(avg_star_xy[0])) + "," + str(int(avg_star_xy[1])), font = font, fill=(255,255,255))
      self.plate_center = (avg_star_xy[0], avg_star_xy[1])
      degree_sign= u'\N{DEGREE SIGN}'
      draw.text((int(self.image_width/2), int(self.image_height/2)), "X", font = font, fill=(255,255,255))
      draw.text((int(self.image_width/2)+15, int(self.image_height/2)), "FOV Center ALT/AZ " + str(int(self.alt_center)) + str(degree_sign) + "/" + str(int(self.az_center)) + str(degree_sign) , font = font, fill=(255,255,255))
      for (name, cons, x,y, cx, cy, myra, mydec,ra, dec, mag,diffra,diffdec) in self.named_stars:
         x = int(float(cx))
         y = int(float(cy))
         nn = str(name) + " " + str(cons)
         draw.text((x+10,y-10), str(nn), font = font, fill=(255,255,255))

      for (x,y,w,h,avg_flux,max_flux,total_flux) in self.starlist:
         x = x + (w/2)
         y = y + (h/2)
         x1 = int(x)-1
         y1 = int(y)-1
         x2 = int(x)+1
         y2 = int(y)+1
         draw.ellipse((x1, y1, x2, y2), fill=255)
      print ("Saving:", star_id_image_file) 

      star_id_image_np = np.asarray(self.star_id_image)
      cv2.imwrite(star_id_image_file, star_id_image_np)


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
      ax.imshow(hdu[0].data, origin='lower', shape = (740,480))

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

   def find_closest_star_in_catalog(self,x,y,myra,mydec,factor,mymag):
      matches = []
      raran = range(int(float(myra)-factor), int(float(myra)+factor))
      decran = range(int(float(mydec)-factor), int(float(mydec)+factor))
      for bname, cons, ra, dec, mag in self.bright_stars:
         cons = cons.decode("utf-8") 
         name = bname.decode("utf-8")
         #print (name, cons)
         if int(float(ra)) in raran and int(float(dec)) in decran and float(mag) <= mymag:
            diff_ra = abs(float(myra) - float(ra))
            diff_dec = abs(float(mydec) - float(dec))
            print ("Possible match: ", name, cons, x,y, myra, mydec, ra,dec,mag, diff_ra, diff_dec)
            matches.append((str(name), str(cons), x,y, myra, mydec,float(ra), float(dec), float(mag), diff_ra, diff_dec))
         else :
            if self.debug == 1:
               print ("No stars close to: ", myra,mydec,ra,dec)
            no = 1
      if len(matches) == 0:
         matches.append((0,0,x,y,myra,mydec,0,0,0,0,0))
         print ("COULD NOT FIND STAR IN CATALOG WITH:", x,y,myra,mydec,factor)
      else:
         matches.sort(key=lambda x: x[10] )
         print("Sorted Matches: ", matches)
         for xxx in matches:
            print (xxx[0], xxx[1], xxx[9], xxx[10])
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
         matches = self.find_closest_star_in_catalog(x,y,radd,decdd,1,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,2,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,3,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,4,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,5,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,6,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,7,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,8,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,9,3)
         if matches[0][0] == 0:
            (matches) = self.find_closest_star_in_catalog(x,y,radd,decdd,10,3)

         if matches[0][0] != 0:
            finds = finds + 1

         # choose brightest if more than 1 match returns
         bright = 10
         best_match = []
         if len(matches) > 1:
            for (name, cons, x,y, myra, mydec,ra, dec, mag, diffra, diffdec) in matches[:]:
               if float(mag) < bright:
                  bright = mag
                  best_matches = [(name, cons, x,y, myra, mydec,ra, dec, mag, diffra, diffdec)]
            matches = best_matches
            (name, cons, x,y, myra, mydec,ra, dec, mag, diffra, diffdec) = matches[0]
         else:
            print(matches[0])
            (name, cons, x,y, myra, mydec,ra, dec, mag, diffra, diffdec) = matches[0]
         print("NAME:", str(name))
         if str(name) != '':
            self.found_stars.append((str(name), str(cons), x,y, myra, mydec,ra, dec, mag, diffra, diffdec))
         else:
            print("NO NAME FOUND:", str(name), x,y)
            self.not_found_stars.append ((str(name) , str(cons), x , y , 0, 0, myra , mydec , 0, 0, 0))
        

      header = "name,lx,ly,cx,cy,lra,ldec,ra,dec,mag,diffra,diffdec"
      print (header)
      for (name, cons, x,y, myra, mydec,ra, dec, mag,diffra,diffdec) in self.found_stars:
         name = str(name)
         if name == "":
            name = "noname"
            print ("No Name on list!")
         else: 
            cor_x, cor_y = self.find_star_match(name, cons)
            self.named_stars.append ((str(name) , str(cons), x , y , cor_x , cor_y , myra , mydec , ra , dec , mag,diffra,diffdec))

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
      self.new_image = self.image
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


   def find_flux(self, x,y,size,writeout=0):
      if self.new_image is None:
         self.new_image = self.image
      box = (x-size,y-size,x+size,y+size)
      #print ("TOTAL FUX: ", total_flux)

      flux_box = self.new_image.crop(box)
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
      np_flux_box.setflags(write=1)
      #print ("BRIGHTEST CENTER: ", cxy,cxx)
      tag = str(x) + "," + str(y) + "/ " + str(cxx) + "," + str(cxy) 
      cv2.putText(np_flux_box, tag, (2, np_flux_box.shape[0] - 2), cv2.FONT_HERSHEY_SIMPLEX, .3, (255, 255, 255), 1)

      cv2.circle(np_flux_box, (cxx,cxy), 10, (255,255,255), 1)
      if writeout == 1:
         cv2.imwrite("/var/www/html/out/cal/flux/" + str(int(total_flux)) + ".jpg", np_flux_box) 

      #cv2.imwrite("/var/www/html/out/cal/flux/tiny" + str(int(total_flux)) + ".jpg", np_flux_box_tiny) 
      return (int(avg_flux), int(max_flux), int(total_flux))

   def add_to_starlist(self, x,y,w,h):
      if self.new_image is None:
         self.new_image = self.image
      print (x,y,w,h)
      x2 = x + w
      y2 = y + h
      px = x
      py = y
      avg_flux, max_flux, total_flux = self.find_flux(int(px), int(py), 10,0)
      
      self.starlist.append([x,y,w,h,avg_flux,max_flux,total_flux])
      for source in self.starlist:
         print ("starlist is")
         print (source)

   def del_from_starlist(self, mx,my):

      xran = range(mx-3, mx+3)
      yran = range(my-10, my+10)
      ok_to_add = 1
      c = 0
      for source in self.starlist[:]:
         tx,ty,w,h,a,m,tm = source
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

      #np_new_image[360+self.padding:360+20+self.padding, 50+self.padding:380+self.padding] = [0]

      np_new_image[335+int(self.padding/2):365+int(self.padding/2), 0+int(self.padding/2):300+int(self.padding/2)] = [0]

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
  
      lower_thresh = self.find_best_thresh(np_new_image, 7)

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
            px = x 
            py = y
            avg_flux, max_flux, total_flux = self.find_flux(int(px), int(py), 10,0)
            #print ("TOTAL FLUX 1: ", total_flux)
            if avg_flux > 0:
               ff = max_flux / avg_flux
            else:
               avg_flux = 1
            if max_flux > 30 and (w < 6 and h < 6) and ff > 2.5:
               cv2.rectangle(np_color_image, (x,y), (x+w, y+h), (0,0,255),2)
               starlist_txt = str(px) + "," + str(py)
               self.starlist.append([x,y,w,h,avg_flux,max_flux,total_flux])
            cc = cc + 1
      #self.starlist_confirmed = self.confirm_found_stars()
      #self.starlist = self.starlist_confirmed
      #print("CONFIRMED STARLIST:", self.starlist_confirmed)
      #for (x,y,w,h,avg_flux,max_flux,total_flux) in self.starlist:
      #   cv2.rectangle(np_color_image, (x,y), (x+w,y+h), (255,255,255),1)
      #   cv2.rectangle(np_color_image, (x-int(w/2),y-int(h/2)), (x+int(w/2), y+int(h/2)), (255,255,255),1)

      # black out
      np_color_image.setflags(write=1)

      np_color_image[335+int(self.padding/2):365+int(self.padding/2), 0+int(self.padding/2):300+int(self.padding/2)] = [255,255,255]
      self.marked_image = Image.fromarray(np_color_image)
      #print(self.starlist)
      #self.displayImage(self.star_image)

   def confirm_found_stars(self):
      temp_starlist = []
      for (x,y,w,h,avg_flux,max_flux,total_flux) in self.starlist:
         box = (x-10,y-10,x+10,y+10)

         avg_flux, max_flux, total_flux  = self.find_flux(int(x), int(y), 20, 1)
        
         if total_flux >= 20 and w > 1 and h > 1:
            temp_starlist.append((x,y,w,h,avg_flux,max_flux,total_flux))

      print("New starlist length:", len(temp_starlist))
      temp_starlist.sort(key=lambda x: x[6], reverse=True)
      final_temp = []
      cc = 0;
      for (x,y,w,h,avg_flux,max_flux,total_flux) in temp_starlist:
         if cc <= 25:
            final_temp.append((x,y,w,h,avg_flux,max_flux,total_flux))
            print("TEMP STARLIST: ", x,y,w,h,avg_flux,max_flux,total_flux) 
         cc = cc + 1 
      return(final_temp)




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
 

      self.star_drawing = Image.new('L', (self.image_width,self.image_height))
      draw = ImageDraw.Draw(self.star_drawing)

      for star in self.starlist:
         x,y,h,w,af,mf,tf  = star
         x = x + (w/2)
         y = y + (h/2)
         #x = x 
         #y = y 
         x1 = int(x)-1
         y1 = int(y)-1
         x2 = int(x)+1
         y2 = int(y)+1
         mff = mf+100

         draw.ellipse((x1, y1, x2, y2), fill=255)
         avg_flux, max_flux, total_flux  = self.find_flux(int(x), int(y), 10)
         fits_data = str(x) + "," + str(y) + "," + str(avg_flux) + "," + str(max_flux) + "\n"
         fp.write(fits_data)
      fp.close()
      print("Saving star drawing here: ", star_drawing_fn) 
      self.star_drawing.save(star_drawing_fn)

      

      #cmd = "/usr/local/astrometry/bin/solve-field " + star_drawing_fn + " --overwrite --width=" + str(self.image_width) + " --height=" + str(self.image_height) + " --scale-units degwidth --scale-low 60 --scale-high 85 --no-remove-lines -cpulimit=15 --odds-to-solve " + str(self.odds_to_solve) + " --code-tolerance " + str(self.code_tolerance) + " 2>&1 > " + solve_out
      cmd = "/usr/local/astrometry/bin/solve-field " + star_drawing_fn + " --overwrite --width=" + str(self.image_width) + " --height=" + str(self.image_height) + " --scale-units degwidth --scale-low 40 --scale-high 85 --no-remove-lines --odds-to-solve " + str(self.odds_to_solve) + " --code-tolerance " + str(self.code_tolerance) + " 2>&1 > " + solve_out
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
         self.azinfo = []
         # ALT AZ
         (alt,az) = self.convert_xy_to_altaz(370,230)
         print ("CENTER ALTAZ:", alt, az)
         data = "CENTER,320,180," + str(az) + "," + str(alt) + "\n"
         self.azinfo.append(("C", 370,230,az,alt))
         self.az_center = az
         self.alt_center = alt
         if alt < 10:
            self.solve_success = 0
         else:

            (alt,az) = self.convert_xy_to_altaz(50,50)
            print ("TL ALTAZ:", alt, az)
            data = data + "TL,0,0," + str(az) + "," + str(alt) + "\n"
            self.azinfo.append(("TL", 0,0,az,alt))

            (alt,az) = self.convert_xy_to_altaz(690,50)
            print ("TR ALTAZ:", alt, az)
            data = data + "TR,640,0," + str(az) + "," + str(alt) + "\n"
            self.azinfo.append(("TR", 690,50,az,alt))

            (alt,az) = self.convert_xy_to_altaz(0,360)
            print ("BL ALTAZ:", alt, az)
            data = data + "BL,0,360," + str(az) + "," + str(alt) + "\n"
            self.azinfo.append(("BL", 50,410,az,alt))

            (alt,az) = self.convert_xy_to_altaz(640,360)
            print ("BR ALTAZ:", alt, az)
            data = data + "BR,640,360," + str(az) + "," + str(alt) + "\n"
            self.azinfo.append(("BR", 50,410,az,alt))

            azout = open(self.az_out_file, "w")
            azout.write(data)
            azout.close() 
            self.save_solution()
            self.update_star_id_image()
         print ("SOLVE SUCCESS")
      else:
         print ("SOLVED FAILED :(")
      if self.solve_success == 0:
         print ("SOLVED FAILED. Solution wrong producing negative ALT/AZ :(")
 

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
      print ("CAL TIME IS: ", self.cal_time)
      print ("LOCATION: ", self.location)
      print ("RA/DEC: ", radd, decdd)
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

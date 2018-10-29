import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import os
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageTk
from PIL import ImageEnhance
import math
from tkinter.filedialog import askopenfilename
import cv2
import CalibrationPage as CP
import brightstardata as bsd



class CalibrationPage():
   def __init__(self, master):
      self.mybsd = bsd.brightstardata()
      self.bright_stars = self.mybsd.bright_stars


      self.master = master
      print ("Cal class init")
      # IMAGE FILE PATHS AND NAMES
      self.image_path = None
      self.catalog_stars = []
      self.wcs_path = None
      self.man_sources = []
      self.data_list = []
      self.image = None
      self.image_cv = None
      self.image_cv_gray = None
      self.new_image = None
      self.starmap_image = None
      self.fireball_image = None
      self.active_image = None
      self.mask_on = None
      self.mask_image = None
      self.cal_time = None
      self.image_width = 1280
      self.image_height = 720
      self.canvas_width = self.image_width
      self.canvas_height = self.image_height
      self.padding = 0
      self.star_thresh = 0
      self.odds_to_solve = 0

      # FRAME 1
      # Build Calibration Layout
      #self.cal_frame1 = tk.Frame(self.master, borderwidth=1, bg='black', height=50, width=1500)
      # info at top of page
      #self.cal_frame1.pack_propagate(0)
      self.image_canvas = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_height, cursor="cross")
      self.button_open = tk.Button(self.master, text="Open File", command=self.OpenImage).grid(row=0,column=0, sticky="w")
      self.filename_label_value = tk.StringVar()
      self.filename_label = tk.Label(self.master, textvariable=self.filename_label_value).grid(row=0,column=1)
      self.button_show_stars = tk.Button(self.master, text="Show Stars", command=self.ShowStars).grid(row=1,column=0, sticky="w")

      self.image_canvas.grid(row=2, column=0, columnspan=2, sticky="w,n", padx=5, pady=5)



      #self.button_open.pack(side=tk.LEFT)
      #self.button_set_location_time = tk.Button(self.cal_frame1, text='Set Loc/Time', command=self.button_set_location_time).pack(padx=1, pady=1, side=tk.LEFT)

      #self.filename_label_value.set("nofile2")

      #self.cal_time_label_value = tk.StringVar()
#      self.cal_time_label = tk.Label(self.cal_frame1, textvariable=self.cal_time).pack(padx=1,pady=1,side=tk.LEFT)
#      self.cal_time_label_value.set("No cal date set yet. ")


#      self.cal_frame1.pack(side=tk.TOP)
#
#      # FRAME 2
#      # image canvas
#      canvas_width = self.image_width
#      canvas_height = self.image_height
#      self.cal_frame2 = tk.Frame(self.master, bg='white', borderwidth=1, width=canvas_width+1, height=canvas_height+1, )
#      self.image_canvas = tk.Canvas(self.cal_frame2, width=canvas_width, height=canvas_height, cursor="cross")
#      self.image_canvas.extra = "image_canvas"
#      self.image_canvas.bind('<Motion>', self.motion)
#      self.image_canvas.pack()
#      self.cal_frame2.extra = 'image_canvas_frame'
#
#      self.image_canvas.bind('<Button-1>', self.mouseClick)
#      self.image_canvas.bind('<Button-3>', self.mouseRightClick)
#      self.cal_frame2.pack(side=tk.TOP)
#
#      # FRAME 3 - Action Buttons
#      self.cal_frame3 = tk.Frame(self.master, bg='blue', height=50, width=self.image_width)
#      self.cal_frame3_unsolved()
#      self.cal_frame3.pack(side=tk.TOP)
#      self.cal_frame3.pack_propagate(0)
#
#
#    # FRAME 4
#
#      self.cal_frame4 = tk.Frame(self.master, bg='blue', height=300, width=self.image_width)
#
#      self.container_far_left = tk.Frame(self.cal_frame4)
#
#      self.fcfl = tk.Frame(self.container_far_left)
#      self.star_thresh_label = tk.Label(self.fcfl, text="Star Threshold" ).pack(padx=1,pady=1,side=tk.TOP)
#      self.e1 = tk.Entry(self.fcfl, textvariable=self.star_thresh)
#      self.e1.insert(0, self.star_thresh)
#      self.e1.pack()
#      self.fcfl.pack(side=tk.TOP)
#
#      self.fcfl2 = tk.Frame(self.container_far_left)
#      self.odds_to_solve_label = tk.Label(self.fcfl2, text="Odds To Solve" ).pack(padx=1,pady=1,side=tk.TOP)
#      self.e2 = tk.Entry(self.fcfl2, textvariable=self.odds_to_solve)
#
#      self.e2.insert(0, self.odds_to_solve)
#      self.e2.pack(side=tk.TOP)
#      self.fcfl2.pack(side=tk.TOP)
#
#      self.fcfl3 = tk.Frame(self.container_far_left)
#      self.code_tolerance = tk.Label(self.fcfl2, text="Code Tolerance" ).pack(padx=1,pady=1,side=tk.TOP)
#      self.e3 = tk.Entry(self.fcfl3, textvariable=self.code_tolerance)
#
#      self.e3.insert(0, ".3")
#      self.e3.pack(side=tk.TOP)
#      self.fcfl3.pack(side=tk.TOP)
#
#
#      self.container_far_left.pack(side=tk.LEFT)
#
#
#      self.container_left = tk.Frame(self.cal_frame4)
#      # Sliders
#      self.field_container = tk.Frame(self.container_left)
#      self.brightness_label = tk.Label(self.field_container, text="Brightness" ).pack(padx=1,pady=1,side=tk.TOP)
#      self.brightness_slider = tk.Scale(self.field_container, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.updateBrightness).pack(padx=1, pady=1, side=tk.BOTTOM)
#      self.field_container.pack(side=tk.TOP)
#
#      self.field_container2 = tk.Frame(self.container_left)
#      contrast_label = tk.Label(self.field_container2, text="Contrast" ).pack(padx=1, pady=1, side=tk.TOP)
#      contrast_slider = tk.Scale(self.field_container2, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.updateContrast ).pack(padx=1, pady=1, side=tk.BOTTOM)
#
#      self.field_container2.pack(side=tk.TOP)
#      self.container_left.pack(side=tk.LEFT)
#
#
#     # Middle Container
#      self.container_middle = tk.Frame(self.cal_frame4)
#
#      self.xy_label_value = tk.StringVar()
#      self.xy_label_value.set("x,y,fa,bp")
#      self.xy_label= tk.Label(self.container_middle, textvariable=self.xy_label_value).pack(padx=1,pady=1,side=tk.TOP)
#
#      self.ra_label_value = tk.StringVar()
#      self.ra_label_value.set("ra,dec")
#      self.ra_label= tk.Label(self.container_middle, textvariable=self.ra_label_value).pack(padx=1,pady=1,side=tk.TOP)
#
#      self.az_label_value = tk.StringVar()
#      self.az_label_value.set("alt,az")
#      self.az_label= tk.Label(self.container_middle, textvariable=self.az_label_value).pack(padx=1,pady=1,side=tk.TOP)
#
#
#      self.container_middle.pack(side=tk.LEFT)
#
#
#      # Right side container!
#      self.container_right = tk.Frame(self.cal_frame4)
#      self.thumbnail_canvas = tk.Canvas(self.container_right, width=100, height=100, cursor="cross")
#      self.thumbnail_canvas.extra = "thumbnail_canvas"
#      self.thumbnail_canvas.pack()
#      self.container_right.pack(side=tk.LEFT)
#
#
#      self.del_button = tk.Button(self.cal_frame4, text='Delete File', command=self.button_delete).pack(padx=1, pady=1, side=tk.LEFT)
#      self.exit_button = tk.Button(self.cal_frame4, text='Exit', command=master.destroy).pack(padx=1, pady=1, side=tk.BOTTOM)
#
#      self.cal_frame4.pack_propagate(0)
#      self.cal_frame4.pack(side=tk.TOP)
#
   def OpenImage(self):
      self.image = self.select_image()
      print ("Cal Date: ", self.cal_time)

      #ALTAZ
      #self.cal_obj.loc_lat = self.loc_lat
      #self.cal_obj.loc_lon = self.loc_lon
      #self.cal_obj.loc_alt = self.loc_alt
      #self.cal_obj.cal_time = self.cal_time


      self.filename_label_value.set( self.image_path)
      self.active_image = "original"
      print ("PATH:", self.image_path)


      self.displayImage(self.image)
      #self.updateContrast(0)

   def button_set_location_time(self):
      print ("Set Location & Time")
      d = MD.MyDialog(root, self)
      root.wait_window(d.top)
      print ("TEST:", self.cal_time)
      self.cal_time_label_value.set(self.cal_time)
      root.update_idletasks()
      print ("TEST:", self.loc_lat)

   def motion(self,event):
      x,y = event.x, event.y
      #print (x,y)
      #if self.image != None and event.widget.extra == "image_canvas_frame":
      if self.image != None :
         box = (x-10,y-10,x+10,y+10)

         crop_box = self.new_image.crop(box)
         crop_box = crop_box.resize((75,75), Image.ANTIALIAS)
         color_crop_box = self.new_image.crop(box)
         color_crop_box = crop_box.resize((75,75), Image.ANTIALIAS)
         np_color_crop_box = np.asarray(color_crop_box)
         gray_crop_box = crop_box.convert('L')

         np_crop_box = np.asarray(gray_crop_box)
         np_crop_box = cv2.GaussianBlur(np_crop_box, (21, 21), 0)
         avg_px = np.average(np_crop_box)
         ax_pixel = np.amax(np_crop_box)
         #print ("AVG PX, BRIGHT PX", avg_px, ax_pixel)

         lower_thresh = ax_pixel - 10

         lower_thresh = avg_px * 1.7
         avg_f, max_f, tot_f = self.cal_obj.find_flux(x,y,10,0)
         _, nice_threshold = cv2.threshold(np_crop_box, lower_thresh, 255, cv2.THRESH_BINARY)
         (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         #print ("CNTS:", len(cnts))

         if len(cnts) > 0:
            xx,yy,w,h = cv2.boundingRect(cnts[0])
            cv2.rectangle(np_color_crop_box, (xx,yy), (xx+w, yy+h), (0,0,255),2)
            crop_box = Image.fromarray(np_color_crop_box)

         xy_val = str(x) + ", " + str(y) + ", " + str(int(avg_f)) + ", " + str(max_f) + ", " + str(tot_f)

         self.xy_label_value.set(xy_val)

         self.displayImageCrop(crop_box)
      else:
         xy_val = "                 "
         self.xy_label_value.set(xy_val)

   def mouseClick(self, event):
      print("Mouse Click")
      x,y = event.x, event.y
      print (event.widget.extra)
      if event.widget.extra == "image_canvas":
         if self.cal_obj.annotated_image != 'None':
            print("clicked at ", x,y)
            (ra, dec, radd, decdd) = self.cal_obj.find_radec_from_xy(x,y)
            ra_str = ra + " " + dec
            self.ra_label_value.set(ra_str)
            print ("ra,dec: ", ra, dec, radd, decdd)
            (alt,az) = self.cal_obj.convert_xy_to_altaz(x,y)
            print ("alt,az: ", alt,az)
            az_str = str(int(alt)) + " " + str(int(az))
            self.az_label_value.set(az_str)
            matches = self.cal_obj.find_closest_star_in_catalog(x,y,radd,decdd,15,4)

   def mouseRightClick(self, event):
      print ("right")
      x,y = event.x, event.y
      if self.mask_on == None or self.mask_on == 0:
         if event.widget.extra == "image_canvas":
            # Check for a delete!
            c = 0
            xran = range(x-10, x+10)
            yran = range(y-10, y+10)
            ok_to_add = 1
            for source in self.man_sources[:]:
               tx,ty = source
               print (tx,ty,x,y)
               if tx in xran and ty in yran:
                  #print ("This source exists, lets remove it!")
                  self.man_sources.remove((tx,ty))
                  print("Deleting From starlist!")
                  self.cal_obj.del_from_starlist(tx,ty)
                  #print ("Source list is : ", self.man_sources)
                  ok_to_add = 0
               c = c + 1
            if ok_to_add == 1:
               self.man_sources.append((x,y))
               print("Adding to starlist!")
               self.cal_obj.add_to_starlist(x,y,5,5)
            #print("Manual Star List Sources: ", self.man_sources)
            self.update_marked_image()
      if self.mask_on == 1:
         if event.widget.extra == "image_canvas":
            # Check for a delete!
            c = 0
            xran = range(x-5, x+5)
            yran = range(y-5, y+5)
            ok_to_add = 1
            for source in self.cal_obj.block_masks:
               tx,ty = source
               print (tx,ty,x,y)
               if tx in xran and ty in yran:
                  print ("This block", x,y," exists, lets remove it!")
                  self.cal_obj.block_masks.remove((tx,ty))
                  ok_to_add = 0
               c = c + 1
            if ok_to_add == 1:
               print ("Adding to block list!")
               self.cal_obj.block_masks.append((x,y))
         print ("Block Mask list is : ", self.cal_obj.block_masks)
         self.update_mask_image()

   def select_image(self):
      self.image_path = askopenfilename(title = "Open File", initialdir='/mnt/ams2/cal/solved/', filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
      felm = self.image_path.split("/")
      file_name = felm[-1]

      if len(self.image_path) > 0:
         self.image_cv = cv2.imread(self.image_path)
         self.image_cv_gray = cv2.cvtColor(self.image_cv, cv2.COLOR_BGR2GRAY)

         ow = self.image_cv.shape[1]
         self.image = Image.fromarray(self.image_cv)
         self.new_image = self.image

         ow = self.image_cv.shape[1]
         oh = self.image_cv.shape[0]

         # add 100 pixels to each side changing
         # original dimensions of 640 / 360
         # to new 840 / 560

         self.image_width = ow+self.padding
         self.image_height= oh+self.padding
      return(self.image)

   def cal_frame3_unsolved(self):
      self.button_container = tk.Frame(self.cal_frame3)
      # FRAME 3 - Action Buttons
      self.find_stars = tk.Button(self.button_container, text='Find Stars', command=self.button_find_stars).pack(padx=1, pady=1, side=tk.LEFT)
      self.solve_field = tk.Button(self.button_container, text='Solve Field', command=self.button_solve_field).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_original = tk.Button(self.button_container, text='Original', command=self.button_show_original).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_enhanced = tk.Button(self.button_container, text='Enhanced', command=self.button_show_enhanced).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_starmap= tk.Button(self.button_container, text='Starmap', command=self.button_show_starmap).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_fireball = tk.Button(self.button_container, text='Add Mask', command=self.button_add_mask).pack(padx=1, pady=1, side=tk.LEFT)
      self.add_stars = tk.Button(self.button_container, text='Add Stars', command=self.button_add_stars).pack(padx=1, pady=1, side=tk.LEFT)
      self.button_container.pack(side=tk.LEFT)

   def button_find_stars(self):


      if self.e1.get() is None or self.e1.get() == "":
         tk.messagebox.showwarning(
            "Please fix threshold. ",
            "Find stars needs a threshold set, somewhere between 3-10 is usually good. If you have light pollution use a higher number.\n"
         )
      print ("find stars handler called")
      self.cal_obj.star_thresh = self.e1.get()
      print (self.cal_obj.star_thresh)

      self.cal_obj.update_image(self.new_image)
      self.cal_obj.find_stars()
      self.displayImage(self.cal_obj.marked_image)
      self.active_image = 'marked_image'
      print(self.cal_obj.starlist)



   def button_solve_field(self):
      print ("YO")

   def button_show_original(self):
      print ("YO")

   def button_show_enhanced(self):
      print ("YO")

   def button_show_starmap(self):
      print ("YO")

   def button_add_mask(self):
      print ("YO")

   def button_add_stars(self):
      print ("YO")

   def updateBrightness(self):
      print ("YO")

   def updateContrast(self):
      print ("YO")

   def button_delete(self):
      print ("YO")

   def ShowStars(self):
      star_file = self.image_path.replace(".jpg", "-star-dist-data.txt")
      self.draw_image = self.image
      font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12, encoding="unic" )
      font2 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 30, encoding="unic" )

      fp = open(star_file, 'r')
      print("STAR_FILE", star_file)
      for line in fp:
         print("MIKE", line)
         exec("self."+line)
      fp.close()
      print(self.star_dist_data)

      print ("YO")
      draw = ImageDraw.Draw(self.draw_image)

      for star_name, iix, iiy, ccx, ccy in self.star_dist_data:
         draw.ellipse((iix-10, iiy-10, iix+10, iiy+10), )
         draw.text((ccx+4,ccy), star_name, font = font, fill=(255,255,255))
         draw.line((ccx-10,ccy,ccx+10,ccy), fill=(255,0,0))
         draw.line((ccx,ccy-10,ccx,ccy+10), fill=(255,0,0))



      self.image_cv_gray = self.block_mask(self.image_cv_gray, (0,self.image_width,self.image_height-80,self.image_height))
      best_thresh = self.find_best_thresh(self.image_cv_gray, 10, 0)
      extra_thresh = 1
      best_thresh = best_thresh + extra_thresh

      _, nice_threshold = cv2.threshold(self.image_cv_gray, best_thresh, 255, cv2.THRESH_BINARY)
      (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      contours = len(cnts)
      cc = 0
      print("CNTS: ", contours)
      starlist = []
      self.catalog_stars = self.parse_astr_star_file()
      extra_starlist = []
      if contours > 0 :
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])
            x2 = int(x + (w/2))
            y2 = int(y + (h/2))
            px = x
            py = y
            found = self.check_if_found(x,y)
            if found == 0:
               draw.ellipse((x2-10, y2-10, x2+10, y2+10), outline=(0,255,0))
               found, matches = self.find_star_in_catalog(x2,y2)
               if found == 1:
                  star_name, ix,iy,cx,cy = matches[0]
                  #draw.ellipse((int(float(cx))-10, int(float(cy))-10, int(float(cx))+10, int(float(cy))+10), outline=(255,255,0))
                  draw.line((cx-10,cy,cx+10,cy), fill=(255,0,0))
                  draw.line((cx,cy-10,cx,cy+10), fill=(255,0,0))
                  corX, corY = self.undistort_point(x,y)
                  print ("CORRECTED: ", x,y,corX,corY)
                  print ("EXTRA STAR FOUND:", found, matches)
                  extra_starlist.append([x,y,w,h])
            cc = cc + 1


      #print(catalog_stars)


      self.displayImage(self.draw_image)

   def find_star_by_name(self, star_name):
      #(status, bname, cons, ra,dec,mag) = find_star_by_name(star_name)
      for bname, cons, ra, dec, mag in self.bright_stars:
         cons = cons.decode("utf-8")
         name = bname.decode("utf-8")
         if name == star_name:
            return(1,name, cons, ra,dec,mag)
      return(0,0,0,0,0,0)

   def find_star_in_catalog(self, x,y):
      found = 0 
      matches = []
      for star_name,cons, ra, dec, mag,  ast_x, ast_y in self.catalog_stars:
         if int(float(ast_x)) - 80 < x < int(float(ast_x)) + 80 and int(float(ast_y)) - 80 < y < int(float(ast_y)) + 80:
            found = 1
            match = (star_name,int(float(x)),int(float(y)),int(float(ast_x)),int(float(ast_y)))
            matches.append(match)
      return(found, matches)

   def check_if_found(self, x,y):
      found = 0
      for star_name, ix,iy,cx,cy in self.star_dist_data:
         if ix - 10 < x < ix + 10 and iy - 10 < y < iy + 10:
            found = 1
      return(found)
      

   def displayImage(self, image):
      self.disp_image = image.resize((1280,720), Image.ANTIALIAS)
      self.tkimage = ImageTk.PhotoImage(self.disp_image)
      self.image_canvas.create_image(int(1280/2),int(720/2), image=self.tkimage )

   def displayImageCrop(self, image):
      self.tkthumb = ImageTk.PhotoImage(image)
      self.thumbnail_canvas.create_image(50,50, image=self.tkthumb)
      #print ("EXTRA: ", self.image_canvas.extra)
      #self.cal_frame2.pack(side=tk.TOP)

   def find_best_thresh(self, image, thresh_limit, type=0):
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

   def block_mask(self, img, info):
      min_x,max_x,min_y,max_y = info
      img.setflags(write=1)
      img[min_y:max_y, min_x:max_x] = [0]
      return(img)

   def parse_astr_star_file(self):
      star_data_file = self.image_path.replace(".jpg", "-stars.txt")
      bright_stars = []
      fp = open(star_data_file, "r")
      for line in fp:
         fields = line.split(" ")
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

            (status, bname, cons, ra,dec,mag) = self.find_star_by_name(star_name)
            data = (star_name,cons, str(ra), str(dec), str(mag),  str(ast_x), str(ast_y))
            bright_stars.append(data)

      return(bright_stars)

   def undistort_point(self,x,y):
      w = self.image_width
      h = self.image_height
      half_w = self.image_width / 2
      half_h = self.image_height / 2
      # optical fov center adj
      #half_w = half_w + 120
      #half_h_ = half_h
      strength = 1.8
      zoom = 1
      correctionRadius = math.sqrt(self.image_width ** 2 + self.image_height ** 2) / strength

      newX = x + half_w
      newY = y + half_h

      distance = math.sqrt(newX ** 2 + newY ** 2)
      r = distance / correctionRadius

      if r == 0:
         theta = 1
      else:
         theta = math.atan(r) * r

      correctedX = half_w + theta / newX * zoom
      correctedY = half_h + theta / newY * zoom

      correctedX = int(float(correctedX))
      correctedY = int(float(correctedY))

      #set color of pixel (x, y) to color of source image pixel at (sourceX, sourceY)
      newX = int(float(newX))
      newY = int(float(newY))
      if correctedY > h-1:
         correctedY = h-1
      if correctedX > w-1:
         correctedX = w-1
      print ("UND:", x,y,correctedX, correctedY)
      return(correctedX, correctedY)

#!/usr/bin/python3
import MFTCalibration as MFTC
import MyDialog as MD 
import tkinter as tk
from tkinter import ttk
import subprocess
import os
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
from PIL import ImageEnhance
from tkinter.filedialog import askopenfilename
import cv2



class calibration_page:
   def __init__(self, master):
      self.master = master
      print ("Cal class init")
      # IMAGE FILE PATHS AND NAMES     
      self.image_path = None
      self.wcs_path = None

      self.image = None
      self.new_image = None
      self.starmap_image = None
      self.fireball_image = None
      self.active_image = None

      self.starlist_array = None
     
      self.cal_time = None
      self.loc_lat = None
      self.loc_lon = None
      self.loc_alt = None
      self.fb_time = None
 
      #self.cal_time = tk.StringVar()
      #self.cal_time.set("YYMMDD HH:MM:SS")
      #self.loc_lat = tk.StringVar()
      #self.loc_lat.set("00")
      #self.loc_lon = tk.StringVar()
      #self.loc_lon.set("00")
      #self.loc_alt = tk.StringVar()
      #self.loc_alt.set("00")
      #self.fb_time= tk.StringVar()
      #self.fb_time.set("00")



      self.cal_obj = MFTC.MFTCalibration()

      # FRAME 1
      # Build Calibration Layout 
      self.cal_frame1 = tk.Frame(self.master, borderwidth=1, bg='black', height=50, width=650)
      # info at top of page
      self.cal_frame1.pack_propagate(0)
      self.button_open = tk.Button(self.cal_frame1, text="Open File", command=self.OpenImage)
      self.button_open.pack(side=tk.LEFT)
      self.button_set_location_time = tk.Button(self.cal_frame1, text='Set Loc/Time', command=self.button_set_location_time).pack(padx=1, pady=1, side=tk.LEFT)

      self.filename_label_value = tk.StringVar()
      self.filename_label_value.set("nofile")
      self.filename_label = tk.Label(self.cal_frame1, textvariable=self.filename_label_value).pack(padx=1,pady=1,side=tk.LEFT)
      self.filename_label_value.set("nofile2")


      self.cal_frame1.pack(side=tk.TOP)

      # FRAME 2
      # image canvas 
      canvas_width = 645
      canvas_height = 365
      self.cal_frame2 = tk.Frame(self.master, bg='white', borderwidth=1, width=canvas_width+1, height=canvas_height+1, )
      self.image_canvas = tk.Canvas(self.cal_frame2, width=canvas_width, height=canvas_height, cursor="cross")
      self.image_canvas.extra = "image_canvas"
      self.image_canvas.bind('<Motion>', self.motion)
      self.image_canvas.pack()
      self.cal_frame2.extra = 'image_canvas_frame'

      self.image_canvas.bind('<Button-1>', self.mouseClick)
      self.image_canvas.bind('<Button-3>', self.mouseRightClick)
      self.cal_frame2.pack(side=tk.TOP)

      # FRAME 3 - Action Buttons
      self.cal_frame3 = tk.Frame(self.master, bg='blue', height=50, width=645)
      self.find_stars = tk.Button(self.cal_frame3, text='Find Stars', command=self.button_find_stars).pack(padx=1, pady=1, side=tk.LEFT)
      self.solve_field = tk.Button(self.cal_frame3, text='Solve Field', command=self.button_solve_field).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_original = tk.Button(self.cal_frame3, text='Original', command=self.button_show_original).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_enhanced = tk.Button(self.cal_frame3, text='Enhanced', command=self.button_show_enhanced).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_starmap= tk.Button(self.cal_frame3, text='Starmap', command=self.button_show_starmap).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_fireball = tk.Button(self.cal_frame3, text='Add Fireball', command=self.button_show_fireball).pack(padx=1, pady=1, side=tk.LEFT)
      self.cal_frame3.pack_propagate(0)
      self.cal_frame3.pack(side=tk.TOP)


      # FRAME 4 

      self.cal_frame4 = tk.Frame(self.master, bg='blue', height=250, width=400)

      self.container_left = tk.Frame(self.cal_frame4)
      # Sliders
      self.field_container = tk.Frame(self.container_left)
      self.brightness_label = tk.Label(self.field_container, text="Brightness" ).pack(padx=1,pady=1,side=tk.TOP)
      self.brightness_slider = tk.Scale(self.field_container, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.updateBrightness).pack(padx=1, pady=1, side=tk.BOTTOM)
      self.field_container.pack(side=tk.TOP)

      self.field_container2 = tk.Frame(self.container_left)
      contrast_label = tk.Label(self.field_container2, text="Contrast" ).pack(padx=1, pady=1, side=tk.TOP)
      contrast_slider = tk.Scale(self.field_container2, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.updateContrast ).pack(padx=1, pady=1, side=tk.BOTTOM)

      self.field_container2.pack(side=tk.TOP)
      self.container_left.pack(side=tk.LEFT)

      # Middle Container
      self.container_middle = tk.Frame(self.cal_frame4)

      self.xy_label_value = tk.StringVar()
      self.xy_label_value.set("x,y,fa,bp")
      self.xy_label= tk.Label(self.container_middle, textvariable=self.xy_label_value).pack(padx=1,pady=1,side=tk.TOP)

      self.ra_label_value = tk.StringVar()
      self.ra_label_value.set("ra,dec")
      self.ra_label= tk.Label(self.container_middle, textvariable=self.ra_label_value).pack(padx=1,pady=1,side=tk.TOP)

      self.az_label_value = tk.StringVar()
      self.az_label_value.set("alt,az")
      self.az_label= tk.Label(self.container_middle, textvariable=self.az_label_value).pack(padx=1,pady=1,side=tk.TOP)


      self.container_middle.pack(side=tk.LEFT)


      # Right side container! 
      self.container_right = tk.Frame(self.cal_frame4)
      self.thumbnail_canvas = tk.Canvas(self.container_right, width=100, height=100, cursor="cross")
      self.thumbnail_canvas.extra = "thumbnail_canvas"
      self.thumbnail_canvas.pack()
      self.container_right.pack(side=tk.LEFT)


      self.exit_button = tk.Button(self.cal_frame4, text='Exit', command=root.destroy).pack(padx=1, pady=1, side=tk.BOTTOM)

      self.cal_frame4.pack_propagate(0)
      self.cal_frame4.pack(side=tk.TOP)

   def motion(self,event):
      x,y = event.x, event.y
      print (x,y)
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
         print ("AVG PX, BRIGHT PX", avg_px, ax_pixel)

         lower_thresh = ax_pixel - 10

         lower_thresh = avg_px * 1.7

         _, nice_threshold = cv2.threshold(np_crop_box, lower_thresh, 255, cv2.THRESH_BINARY)
         (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         #print ("CNTS:", len(cnts))

         if len(cnts) > 0:
            xx,yy,w,h = cv2.boundingRect(cnts[0])
            cv2.rectangle(np_color_crop_box, (xx,yy), (xx+w, yy+h), (0,0,255),2)
            crop_box = Image.fromarray(np_color_crop_box)

         xy_val = str(x) + ", " + str(y) + ", " + str(int(avg_px)) + ", " + str(ax_pixel)

         self.xy_label_value.set(xy_val)

         self.displayImageCrop(crop_box)
      else:
         xy_val = "                 "
         self.xy_label_value.set(xy_val)


   def button_set_location_time(self):
      print ("Set Location & Time")
      d = MD.MyDialog(root, self.cal_time, self.loc_lat, self.loc_lon, self.loc_alt, self.fb_time, "Set Time and Location", "Calibration Time in UTC", "Latitude", "Longitude", "Altitude", "Fireball Time in UTC")
      self.cal_time = d.cal_time
      print ("CAL TIME: ", self.cal_time)
      #self.loc_lat = d.loc_lat
      #self.loc_lon= d.loc_lon
      #self.loc_alt = d.loc_alt
      #self.fb_time = d.fb_time

      root.wait_window(d.top)

   def button_show_fireball(self):
      print ("Show Fireball")
      self.active_image = 'fireball'
   def button_solve_field(self):
      print ("solve field handler called")
      self.cal_obj.update_path(self.image_path)
      self.cal_obj.solve_field()
      #self.displayImage(self.cal_obj.star_drawing)
      #self.annotated_image = self.cal_obj.annotated_image
      self.starmap_image= self.cal_obj.annotated_image
      self.displayImage(self.cal_obj.annotated_image)
      self.active_image = 'starmap'

   def button_find_stars(self):
      print ("find stars handler called")
      self.cal_obj.update_image(self.new_image)
      self.cal_obj.find_stars()
      self.displayImage(self.cal_obj.marked_image)
      self.active_image = 'marked_image'

   def button_show_original(self):
      self.displayImage(self.image)
      print ("Show original")
      self.active_image = 'original'
   def button_show_enhanced(self):
      self.displayImage(self.new_image)
      self.active_image = 'enhanced'
      print ("Show enhanced")
   def button_show_starmap(self):
      self.displayImage(self.starmap_image)
      self.active_image = 'starmap'
      print ("Show starmap")

   def updateBrightness(self, value):
      if int(float(value)) < 0:
         value = int(float(value)) * -1
         new_value = 1 - (value / 100)
      else:
         new_value = (int(float(value)) / 10) + 1
      if value == 0:
         new_value = 1

      if self.image != None:
         # put handler here for active image
         if self.active_image == 'original':
            enhancer = ImageEnhance.Brightness(self.image)
            self.new_image = enhancer.enhance(new_value)
         if self.active_image == 'enhanced':
            enhancer = ImageEnhance.Brightness(self.new_image)
            self.new_image = enhancer.enhance(new_value)
         if self.active_image == 'starmap':
            enhancer = ImageEnhance.Brightness(self.starmap_image)

         enhanced_image = enhancer.enhance(new_value)
         self.displayImage(enhanced_image)
         print(self.image_canvas.extra)

   def updateContrast(self, value):
      if int(float(value)) < 0:
         value = int(float(value)) * -1
         new_value = 1 - (value / 100)
      else:
         new_value = (int(float(value)) / 10) + 1
      if value == 0:
         new_value = 1

      if self.image != None:
         if self.active_image == 'original':
            enhancer = ImageEnhance.Contrast(self.image)
            self.new_image = enhancer.enhance(new_value)
         if self.active_image == 'enhanced':
            enhancer = ImageEnhance.Contrast(self.new_image)
            self.new_image = enhancer.enhance(new_value)
         if self.active_image == 'starmap':
            enhancer = ImageEnhance.Contrast(self.starmap_image)
         enhanced_image = enhancer.enhance(new_value)
         self.displayImage(enhanced_image)


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


   def mouseRightClick(self, event):
      print ("right")

   def displayImage(self, image):
      print (self.image_path)
      self.tkimage = ImageTk.PhotoImage(image)
      self.image_canvas.create_image(320,180, image=self.tkimage )
      print ("EXTRA: ", self.image_canvas.extra)
      #self.cal_frame2.pack(side=tk.TOP)

   def displayImageCrop(self, image):
      self.tkthumb = ImageTk.PhotoImage(image)
      self.thumbnail_canvas.create_image(50,50, image=self.tkthumb)
      print ("EXTRA: ", self.image_canvas.extra)
      #self.cal_frame2.pack(side=tk.TOP)
      


   def select_image(self):
      self.image_path = askopenfilename(title = "Open File", initialdir='/var/www/html/out/cal')
      if len(self.image_path) > 0:
         self.image = cv2.imread(self.image_path)
         self.image = Image.fromarray(self.image)
         self.new_image = self.image
      return(self.image)

   def OpenImage(self):
      self.image = self.select_image()
      self.new_image = self.image
      self.filename_label_value.set( self.image_path)
      self.active_image = "original"
      print ("PATH:", self.image_path)

      if self.starlist_array != None:
         print("Clear starlist")
         self.clear_starlist()
      else:
         print ("starlist empty")

      self.displayImage(self.image)
      self.updateContrast(0)



class FireballGUI:
   def __init__(self, parent, *args, **kwargs):
      
      root.title("Mike's Fireball Tools")
      note = ttk.Notebook(root)
      self.make_tabs(note)

   def make_tabs(self, note):
      tab1 = tk.Frame(note, width=700, height=600)
      example = calibration_page(tab1)
      note.add(tab1, text = "Calibration")
      tab1.pack_propagate(0)
      tab2 = tk.Frame(note)
      tab3 = tk.Frame(note)
      tab4 = tk.Frame(note)
      tab5 = tk.Frame(note)
      note.add(tab2, text = "Reduction")
      note.add(tab3, text = "Solution")
      note.add(tab4, text = "Config")
      note.add(tab5, text = "Devices")
      note.pack()






root = tk.Tk()

FireballGUI(root)
root.mainloop()



#!/usr/bin/python3
import MFTCalibration as MFTC
import MyDialog as MD 
#from amscommon import read_config
import tkinter as tk
from amscommon import read_config
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
from tkinter.filedialog import askopenfilename
#import tkSimpleDialog as tks
import cv2

class calibration_page:
   def __init__(self, master):
      self.master = master
      print ("Cal class init")
      # IMAGE FILE PATHS AND NAMES     
      self.image_path = None
      self.wcs_path = None
      self.man_sources = []
      self.data_list = []
      self.image = None
      self.new_image = None
      self.starmap_image = None
      self.fireball_image = None
      self.active_image = None
      self.mask_on = None
      self.mask_image = None

      self.starlist_array = None
      self.padding = 0
      self.image_width = 640 + (self.padding * 2)  # 840
      self.image_height = 360 + (self.padding * 2) # 560

      cam_num = 1 
      config_file = "/home/ams/fireball_camera/conf/config-" + str(cam_num) + ".txt"
      config = read_config(config_file)
     
      self.cal_time = None
      self.obs_code = None
      self.loc_lat = config['device_lat']
      self.loc_lon = config['device_lng'] 
      self.loc_alt = config['device_alt'] 
      self.fb_dt = None

      self.star_thresh = 7
      self.odds_to_solve = 10000
      self.code_tolerance = .3


      # FRAME 1
      # Build Calibration Layout 
      self.cal_frame1 = tk.Frame(self.master, borderwidth=1, bg='black', height=50, width=650)
      # info at top of page
      self.cal_frame1.pack_propagate(0)
      self.button_open = tk.Button(self.cal_frame1, text="Open File", command=self.OpenImage)
      self.button_open.pack(side=tk.LEFT)
      self.button_set_location_time = tk.Button(self.cal_frame1, text='Set Loc/Time', command=self.button_set_location_time).pack(padx=1, pady=1, side=tk.LEFT)

      self.filename_label_value = tk.StringVar()
      self.filename_label = tk.Label(self.cal_frame1, textvariable=self.filename_label_value).pack(padx=1,pady=1,side=tk.LEFT)
      self.filename_label_value.set("nofile2")

      self.cal_time_label_value = tk.StringVar()
      self.cal_time_label = tk.Label(self.cal_frame1, textvariable=self.cal_time).pack(padx=1,pady=1,side=tk.LEFT)
      self.cal_time_label_value.set("No cal date set yet. ")


      self.cal_frame1.pack(side=tk.TOP)

      # FRAME 2
      # image canvas 
      canvas_width = self.image_width
      canvas_height = self.image_height
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
      self.cal_frame3 = tk.Frame(self.master, bg='blue', height=50, width=self.image_width)
      self.cal_frame3_unsolved()
      self.cal_frame3.pack(side=tk.TOP)
      self.cal_frame3.pack_propagate(0)

      # FRAME 4 

      self.cal_frame4 = tk.Frame(self.master, bg='blue', height=300, width=self.image_width)

      self.container_far_left = tk.Frame(self.cal_frame4)

      self.fcfl = tk.Frame(self.container_far_left)
      self.star_thresh_label = tk.Label(self.fcfl, text="Star Threshold" ).pack(padx=1,pady=1,side=tk.TOP)
      self.e1 = tk.Entry(self.fcfl, textvariable=self.star_thresh)
      self.e1.insert(0, self.star_thresh)
      self.e1.pack()
      self.fcfl.pack(side=tk.TOP)

      self.fcfl2 = tk.Frame(self.container_far_left)
      self.odds_to_solve_label = tk.Label(self.fcfl2, text="Odds To Solve" ).pack(padx=1,pady=1,side=tk.TOP)
      self.e2 = tk.Entry(self.fcfl2, textvariable=self.odds_to_solve)

      self.e2.insert(0, self.odds_to_solve)
      self.e2.pack(side=tk.TOP)
      self.fcfl2.pack(side=tk.TOP)

      self.fcfl3 = tk.Frame(self.container_far_left)
      self.code_tolerance = tk.Label(self.fcfl2, text="Code Tolerance" ).pack(padx=1,pady=1,side=tk.TOP)
      self.e3 = tk.Entry(self.fcfl3, textvariable=self.code_tolerance)

      self.e3.insert(0, ".3")
      self.e3.pack(side=tk.TOP)
      self.fcfl3.pack(side=tk.TOP)


      self.container_far_left.pack(side=tk.LEFT)


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


      self.del_button = tk.Button(self.cal_frame4, text='Delete File', command=self.button_delete).pack(padx=1, pady=1, side=tk.LEFT)
      self.exit_button = tk.Button(self.cal_frame4, text='Exit', command=root.destroy).pack(padx=1, pady=1, side=tk.BOTTOM)

      self.cal_frame4.pack_propagate(0)
      self.cal_frame4.pack(side=tk.TOP)

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

   def cal_frame3_solved(self):
      # FRAME 3 - Action Buttons
      self.button_container = tk.Frame(self.cal_frame3)
      # FRAME 3 - Action Buttons
      self.show_original = tk.Button(self.button_container, text='Original', command=self.button_show_original).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_enhanced = tk.Button(self.button_container, text='Enhanced', command=self.button_show_enhanced).pack(padx=1, pady=1, side=tk.LEFT)
      self.find_stars = tk.Button(self.button_container, text='Marked Stars', command=self.button_show_all_stars).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_starmap= tk.Button(self.button_container, text='Constellations', command=self.button_show_starmap).pack(padx=1, pady=1, side=tk.LEFT)
      self.show_starmap= tk.Button(self.button_container, text='Star Chart', command=self.button_show_starmap).pack(padx=1, pady=1, side=tk.LEFT)
      self.solve_field = tk.Button(self.button_container, text='Resolve', command=self.button_solve_field).pack(padx=1, pady=1, side=tk.LEFT)
      self.button_container.pack(side=tk.LEFT)




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

   def button_delete(self):

      if self.image_path is None:
         tk.messagebox.showwarning(
            "Nothing to do bro. ",
            "Cannot delete file when nothing is open\n" 
         )
      else:
         result = tk.messagebox.askokcancel("Delete Calibration File","Would you like to delete this file and all assocaited data?")
         if result is True:
            print ("Deleting files.", result)
            clean_path = self.image_path.replace(".jpg", "*")
            cmd = "rm " + str(clean_path)
            print(cmd)
            os.system(cmd)
            orig_path = self.image_path.replace("astrometry", "good")
            cmd = "rm " + str(orig_path)
            print(cmd)
            os.system(cmd)



         else:
            print ("Np man.")

   def button_add_mask(self):
      self.image_canvas.config(cursor="circle")
      self.mask_on = 1

   def button_add_stars(self):
      self.image_canvas.config(cursor="cross")
      self.mask_on = 0 


   def button_set_location_time(self):
      print ("Set Location & Time")
      d = MD.MyDialog(root, self)
      root.wait_window(d.top)
      print ("TEST:", self.cal_time)
      self.cal_time_label_value.set(self.cal_time)
      root.update_idletasks()
      print ("TEST:", self.loc_lat)

      #print (d.result() )


   def button_show_fireball(self):
      print ("Show Fireball")
      self.active_image = 'fireball'

   def button_solve_field(self):
      result = None
      print ("solve field handler called")
      self.cal_obj.odds_to_solve = self.e2.get()
      self.cal_obj.code_tolerance = self.e3.get()
      self.cal_obj.update_path(self.image_path)


      self.cal_obj.solved_file = self.image_path.replace(".jpg", "-sd.solved")
      print ("solved? : ", self.cal_obj.solved_file)
      if os.path.isfile(self.cal_obj.solved_file):
         print ("already solved)")
         self.solve_success = 1

         #root.wait_window(d.top)
         root.update_idletasks()
         while result is None:
            result = tk.messagebox.askokcancel("Field already solved.", "This field has already been solved. Do you want to solve it again?")

            #self.displayImage(self.cal_obj.star_drawing)
            #self.annotated_image = self.cal_obj.annotated_image
         if result == 1:
            self.cal_obj.solve_field()
            self.starmap_image= self.cal_obj.annotated_image
            self.displayImage(self.cal_obj.annotated_image)
            self.active_image = 'starmap'
            self.update_star_id_image()
      else:
         self.cal_obj.solve_field()
         self.starmap_image= self.cal_obj.annotated_image
         self.displayImage(self.cal_obj.annotated_image)
         self.active_image = 'starmap'
         self.update_star_id_image()


   def button_show_all_stars(self):
      print ("Show all stars")
      self.update_star_id_image()

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
            (alt,az) = self.cal_obj.convert_xy_to_altaz(x,y)
            print ("alt,az: ", alt,az)
            az_str = str(int(alt)) + " " + str(int(az))
            self.az_label_value.set(az_str)
            matches = self.cal_obj.find_closest_star_in_catalog(x,y,radd,decdd,15,4)


   def update_star_id_image(self):

      self.cal_obj.update_star_id_image()
      if self.cal_obj.solve_success == 1:
         self.displayImage(self.cal_obj.star_id_image)
      else:
         print ("Cal obj success is 0")

   def update_mask_image(self):
      self.mask_image = self.image.convert('L')
      self.mask_image = np.asarray(self.image) 
      print ("Total masked areas: ", len(self.cal_obj.block_masks))
      for x,y in self.cal_obj.block_masks:
         cv2.circle(self.mask_image, (x,y), 5, (255), -1)
         min_x = x - 10
         max_x = x + 10
         min_y = y - 10
         max_y = y + 10
         print ("Mask around : ", min_x,max_x,min_y,max_y)
         self.mask_image.setflags(write=1)
         self.mask_image[min_y:max_y, min_x:max_x] = [255]
      self.mask_image= Image.fromarray(self.mask_image)
      print ("Display the mask image.")
      self.active_image = 'mask'
      self.displayImage(self.mask_image)

   def update_marked_image(self):
      self.cal_obj.marked_image = self.image
      marked_image_np = np.asarray(self.cal_obj.marked_image) 
      for x,y,w,h,af,mf,tf in self.cal_obj.starlist:
         print("Drawing circle")
         cv2.circle(marked_image_np, (x,y), 5, (255), -1)
      self.cal_obj.marked_image = Image.fromarray(marked_image_np)
      yo = Image.fromarray(marked_image_np)
      self.active_image = 'marked_image'
      self.displayImage(yo)
      

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


   def displayImage(self, image):
      #print (self.image_path)
      #print ("DisplayImage")
      self.tkimage = ImageTk.PhotoImage(image)

      self.image_canvas.create_image(int(self.image_width/2),int(self.image_height/2), image=self.tkimage )
      #print ("EXTRA: ", self.image_canvas.extra)
      #self.cal_frame2.pack(side=tk.TOP)

   def displayImageCrop(self, image):
      self.tkthumb = ImageTk.PhotoImage(image)
      self.thumbnail_canvas.create_image(50,50, image=self.tkthumb)
      #print ("EXTRA: ", self.image_canvas.extra)
      #self.cal_frame2.pack(side=tk.TOP)
      


   def select_image(self):
      self.image_path = askopenfilename(title = "Open File", initialdir='/var/www/html/out/cal/', filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
      felm = self.image_path.split("/")
      file_name = felm[-1]

      cmd = "cp " + self.image_path + " /var/www/html/out/cal/astrometry/" + file_name
      os.system(cmd)
      self.image_path = "/var/www/html/out/cal/astrometry/" + file_name
      print (cmd)

      if len(self.image_path) > 0:
         self.image_np = cv2.imread(self.image_path)
         ow = self.image_np.shape[1]
         if ow == 1920:
            self.image_np = cv2.resize(self.image_np, (640, 360))
         self.image = Image.fromarray(self.image_np)
         self.new_image = self.image


         ow = self.image_np.shape[1]
         oh = self.image_np.shape[0]

         # add 100 pixels to each side changing 
         # original dimensions of 640 / 360
         # to new 840 / 560 
 
         self.image_width = ow+self.padding
         self.image_height= oh+self.padding
         if (ow != self.image_width and oh != self.image_height): 
            canvas_size = oh+self.padding,ow+self.padding,3
            canvas = np.zeros(canvas_size,dtype=np.uint8)
            canvas.fill(0)
            canvas[int(self.padding/2):oh+int(self.padding/2),int(self.padding/2):ow+int(self.padding/2)] = self.image_np
            self.image_np = canvas
            self.image = Image.fromarray(self.image_np)
            self.new_image = self.image
            cv2.imwrite(self.image_path, self.image_np)

            self.image_np = cv2.imread(self.image_path)
            self.image = Image.fromarray(self.image_np)
            self.new_image = self.image

      
      solved_file = self.image_path.replace(".jpg", "-sd.solved")

      if os.path.isfile(solved_file):
         print ("already solved)")

         result = tk.messagebox.askokcancel("Image already solved.", "This image has already been solved. Do you want to load the know solution? Press cancel to solve it again?")
         if result is True:
            print ("Using previous solve.")
            self.new_image = self.image
            self.cal_obj = MFTC.MFTCalibration()
            self.cal_obj.update_path(self.image_path)
            self.cal_obj.new_image = self.image
          
            self.cal_time = self.cal_obj.parse_file_date(self.image_path)
            self.cal_obj.image_width = self.image_np.shape[1]
            self.cal_obj.image_height = self.image_np.shape[0]
            self.cal_obj.load_solution() 
            self.cal_obj.solve_success == 1
            #print(self.solve_field)
            #self.hide_widget(self.solve_field)
            #self.cal_frame3.destroy()
            self.button_container.pack_forget()

            self.cal_frame3_solved()
            self.starmap_image= self.cal_obj.annotated_image
         else: 
            print ("Ignoring previous solve.")
            self.new_image = self.image
            self.cal_obj = MFTC.MFTCalibration()
            self.cal_obj.update_path(self.image_path)
            self.cal_obj.new_image = self.image
            self.cal_time = self.cal_obj.parse_file_date(self.image_path)
            self.cal_obj.image_width = self.image_np.shape[1]
            self.cal_obj.image_height = self.image_np.shape[0]
            if self.starlist_array != None:
               print("Clear starlist")
               self.clear_starlist()
            else:
               print ("starlist empty")
      # image has not been solved yet... 
      else:
         print ("Never been solved.")
         self.new_image = self.image
         self.cal_obj = MFTC.MFTCalibration()
         self.cal_obj.update_path(self.image_path)
         self.cal_obj.new_image = self.image
         self.cal_time = self.cal_obj.parse_file_date(self.image_path)
         self.cal_obj.image_width = self.image_np.shape[1]
         self.cal_obj.image_height = self.image_np.shape[0]

         if self.starlist_array != None:
            print("Clear starlist")
            self.clear_starlist()
         else:
            print ("starlist empty")


      return(self.image)

   def OpenImage(self):
      self.image = self.select_image()
      print ("Cal Date: ", self.cal_time)

      #ALTAZ
      self.cal_obj.loc_lat = self.loc_lat 
      self.cal_obj.loc_lon = self.loc_lon 
      self.cal_obj.loc_alt = self.loc_alt 
      self.cal_obj.cal_time = self.cal_time 


      self.filename_label_value.set( self.image_path)
      self.active_image = "original"
      print ("PATH:", self.image_path)


      self.displayImage(self.image)
      self.updateContrast(0)



class FireballGUI:
   def __init__(self, parent, *args, **kwargs):
      
      root.title("Mike's Fireball Tools")
      note = ttk.Notebook(root)
      self.make_tabs(note)

   def make_tabs(self, note):
      tab1 = tk.Frame(note, width=760, height=800)
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



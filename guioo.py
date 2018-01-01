#!/usr/bin/python3

import os
import numpy as np
from tkinter import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
from PIL import ImageEnhance
from tkinter.filedialog import askopenfilename
import cv2

# OOO 
# 
# Break down the problem into fundemental groups (classes) 
# 
# Main Interface
# Calibration Image Handling
#   finding stars
#   solving the plate
# Video Handling
#   extracting all frames
#   making stack of frames
#   reducing stack with calibration

class Calibration:
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
            #self.starlist_value = Label(self.master, text=starlist_txt , bg="gray80")
            #self.starlist_value.grid(row=6+i, column=0)
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
      cmd = "/usr/bin/jpegtopnm " + self.path + "|/usr/local/astrometry/bin/plot-constellations -w " + self.wcs_file + " -o " + self.constellation_file + " -i - -C -G 600"

      print (cmd)
      os.system(cmd)

      cmd = "/usr/local/astrometry/bin/wcsinfo " + self.wcs_file + " > " + self.star_data_file
      os.system(cmd)

      #self.astr_path = self.path.replace(".jpg", "-sd-objs.png")
      self.np_annotated_image = cv2.imread(self.constellation_file)
      self.annotated_image = Image.fromarray(self.np_annotated_image)



   def hello(self):
      return("some func says hi")

class FireballGUI:
   def __init__(self, master):
      self.master = master
      master.title("Mike's Fireball Tools")

      self.path = None
      self.image = None
      self.new_image = None
      self.star_image = None
      self.star_drawing= None
      self.starlist_array = [] 


      # Menu
      menu = Menu(master)
      master.config(menu=menu)
      master.bind('<Motion>', self.motion)
      master.bind("<ButtonPress-1>", self.ms_create_rect)
      master.bind("<ButtonRelease-1>", self.ms_create_rect)
      master.extra="main app"

      self.cal_obj = Calibration()

      filemenu = Menu(menu)
      menu.add_cascade(label="File", menu=filemenu)
      filemenu.add_command(label="Open Image", command=self.OpenImage)
      filemenu.add_command(label="Open Video", command=self.OpenVideo)
      filemenu.add_separator()
      filemenu.add_command(label="Exit", command=master.quit)

      brightness_slider = Scale(master, from_=-100, to=100, orient=HORIZONTAL, command=self.updateBrightness, bg="gray80")
      brightness_slider.grid(row=1, column=1, padx=2, pady=2 )
      brightness_slider.extra="Brightness Slider"
      brightness_label = Label(master, text="Brightness", bg="gray80")
      brightness_label.grid(row=1, column=0)
      brightness_label.extra="Brightness Label"

      contrast_slider = Scale(master, from_=-100, to=100, orient=HORIZONTAL, command=self.updateContrast, bg="gray80")
      contrast_slider.grid(row=2, column=1, padx=2, pady=2 )
      contrast_slider.extra="Contrast Slider"
      contrast_label = Label(master, text="Contrast", bg="gray80")
      contrast_label.grid(row=2, column=0)
      contrast_label.extra = "contrast"
      brightness_label.extra="Contrast Label"

      #button = Button(master, text="Find Stars", fg="red", command=self.detect_all_stars, bg="gray80")
      button = Button(master, text="Find Stars", fg="red", command=self.find_stars_handler, bg="gray80")
      button.grid(row=4, column=0, padx=2, pady=2)
      button.extra = "find stars"

      button = Button(master, text="Solve Field", fg="red", command=self.solve_field_handler, bg="gray80")
      button.grid(row=4, column=1, padx=2, pady=2)
      button.extra = "solve field"

      xy_label = Label(master, text="x,y", bg="gray80")
      xy_label.grid(row=3, column=0)
      xy_label.extra = "xy"
      xy_value = Label(master, text="0,0", bg="gray80")
      xy_value.extra = "xy"
      xy_value.grid(row=3, column=1)

      starlist_label = Label(master, text="starlist", bg="gray80")
      starlist_label.grid(row=5, column=0)
      starlist_label.extra = "starlist"

      starlist_value = Label(master, text="", bg="gray80")
      starlist_value.extra = "starlist"
      starlist_value.grid(row=6, column=0)

   def find_stars_handler(self):
      print ("find stars handler called")
      self.cal_obj.update_image(self.new_image)
      self.cal_obj.find_stars()
      self.displayImage(self.cal_obj.marked_image)

   def solve_field_handler(self):
      print ("solve field handler called")
      self.cal_obj.update_path(self.path)
      self.cal_obj.solve_field()
      #self.displayImage(self.cal_obj.star_drawing)
      self.image = self.cal_obj.annotated_image
      self.displayImage(self.cal_obj.annotated_image)


      #print ("what is: ", what)

   def motion(self,event):
      x,y = event.x, event.y
      if self.image != None and event.widget.extra == "pic":
         box = (x-10,y-10,x+10,y+10)

         crop_box = self.new_image.crop(box)
         crop_box = crop_box.resize((75,75), Image.ANTIALIAS)
         gray_crop_box = crop_box.convert('L')

         np_crop_box = np.asarray(gray_crop_box)
         np_crop_box = cv2.GaussianBlur(np_crop_box, (21, 21), 0)
         avg_px = np.average(np_crop_box)
         ax_pixel = np.amax(np_crop_box)
         #print ("AVG PX, BRIGHT PX", avg_px, ax_pixel)

         lower_thresh = ax_pixel - 10

         lower_thresh = avg_px * 1.7

         _, nice_threshold = cv2.threshold(np_crop_box, lower_thresh, 255, cv2.THRESH_BINARY)
         (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         #print ("CNTS:", len(cnts))

         if len(cnts) > 0:
            xx,yy,w,h = cv2.boundingRect(cnts[0])
            cv2.rectangle(np_crop_box, (xx,yy), (xx+w, yy+h), (0,0,255),2)
            crop_box = Image.fromarray(np_crop_box)

         xy_val = str(x) + ", " + str(y) + ", " + str(int(avg_px)) + ", " + str(ax_pixel)
         xy_value = Label(self.master, text=xy_val)
         xy_value.grid(row=3, column=1)
         xy_value.extra = "xyv"

      #   print ("AXPIX", ax_pixel)
         self.displayImageCrop(crop_box)

   def ms_xaxis(self, event):
      return (event.x - 1), (event.y - 1) # x1, y1

   def ms_yaxis(self, event):
      return (event.x + 1), (event.y + 1) # x2, y2

   def ms_create_rect(self, event):
      x1, y1 = self.ms_xaxis(event)
      x2, y2 = self.ms_yaxis(event)
      #master.create_rectangle(x1,y1,x2,y2,fill='Black')

   def select_image(self):
      self.path = askopenfilename(title = "Open File", initialdir='/var/www/html/out/cal')
      if len(self.path) > 0:
         self.image = cv2.imread(self.path)
         self.image = Image.fromarray(self.image)
         self.new_image = self.image
      return(self.image)

   def updateBrightness(self, value):
      if int(value) < 0:
         value = int(value) * -1
         new_value = 1 - (value / 100)
      else:
         new_value = (int(value) / 10) + 1
      if value == 0:
         new_value = 1

      if self.image != None:
         enhancer = ImageEnhance.Brightness(self.image)
         self.new_image = enhancer.enhance(new_value)
         self.displayImage(self.new_image)

   def updateContrast(self, value):
      if int(value) < 0:
         value = int(value) * -1
         new_value = 1 - (value / 100)
      else:
         new_value = (int(value) / 10) + 1
      if value == 0:
         new_value = 1

      if self.image != None:
         enhancer = ImageEnhance.Contrast(self.image)
         self.new_image = enhancer.enhance(new_value)
         self.displayImage(self.new_image)

   def OpenImage(self):
      image = self.select_image()
      self.new_image = self.image


      if self.starlist_array != None:
         print("Clear starlist")
         self.clear_starlist()
      else:
         print ("starlist empty")

      self.displayImage(image)
      self.updateContrast(0)


   def displayImageCrop(self, crop_image):
      tkimage = ImageTk.PhotoImage(crop_image)
      imageFrame = Label(image=tkimage)
      imageFrame.image = tkimage
      imageFrame.grid(row=1, column=4, padx=2, pady=2, rowspan=4)
      imageFrame.extra = "pic"

   def displayImage(self, image):
      tkimage = ImageTk.PhotoImage(image)
      imageFrame = Label(image=tkimage, bg="gray80")
      imageFrame.image = tkimage
      imageFrame.grid(row=0, column=0, padx=10, pady=10, columnspan=5)
      imageFrame.extra = "pic"

   def OpenVideo(self):
      print ("BLAH")

   def clear_starlist(self):
      starlist_array = []
      for label in self.master.grid_slaves():
         if int(label.grid_info()["row"])>=6:
            #print ("removing...")
            label.grid_forget()








root = Tk()

fireball_gui = FireballGUI(root)
root.mainloop()

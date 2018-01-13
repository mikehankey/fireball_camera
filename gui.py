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

image = None
new_image = None 
starlist_array = None 

def ms_xaxis(event):
   return (event.x - 1), (event.y - 1) # x1, y1

def ms_yaxis(event):
   return (event.x + 1), (event.y + 1) # x2, y2

def ms_create_rect(event):
   x1, y1 = ms_xaxis(event)
   x2, y2 = ms_yaxis(event)
   master.create_rectangle(x1,y1,x2,y2,fill='Black')

def select_image():
   global path
   global image
   global new_image
   global starlist_array 
   path = askopenfilename(title = "Open File", initialdir='/var/www/html/out/cal')
   if len(path) > 0:
      image = cv2.imread(path)
      image = Image.fromarray(image)
      new_image = image
   return(image)

def updateBrightness(value):
   global new_image
   if int(value) < 0:
      value = int(value) * -1
      new_value = 1 - (value / 100)
   else:
      new_value = (int(value) / 10) + 1
   if value == 0:
      new_value = 1

   print ("YO", value, new_value)
   if image != None:
      enhancer = ImageEnhance.Brightness(image)
      new_image = enhancer.enhance(new_value)
  #    image = new_image
      displayImage(new_image)

def updateContrast(value):
   global new_image
   if int(value) < 0:
      value = int(value) * -1
      new_value = 1 - (value / 100)
   else:
      new_value = (int(value) / 10) + 1
   if value == 0:
      new_value = 1

   print ("YO", value, new_value)
   if image != None:
      enhancer = ImageEnhance.Contrast(image)
      new_image = enhancer.enhance(new_value)
      #image = new_image
      displayImage(new_image)

def detect_all_stars():
   global new_image
   global starlist_array 
   starlist_array = []
   gray_new_image = new_image.convert('L')
   np_new_image = np.asarray(gray_new_image)
   np_new_image.setflags(write=1)
   np_new_image[340:360, 0:230] = [0]

   avg_px = np.average(np_new_image) 
   ax_pixel = np.amax(np_new_image)
   print ("AVG PX, BRIGHT PX", avg_px, ax_pixel)

   lower_thresh = ax_pixel - 10

   lower_thresh = avg_px * 3 

   #np_new_image = cv2.GaussianBlur(np_new_image, (1, 1), 0)
   _, nice_threshold = cv2.threshold(np_new_image, lower_thresh, 255, cv2.THRESH_BINARY)
   (_, cnts, xx) = cv2.findContours(nice_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   contours = len(cnts)
   x,y,w,h = 0,0,0,0
   starlist_value = ""
   star_image = image
   draw = ImageDraw.Draw(star_image)
   if contours > 0:
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         print (x,y,w,h)
         x2 = x + w
         y2 = y + h
         px = int(x + (w/2))
         py = int(y + (h/2))
         cv2.rectangle(np_new_image, (x,y), (x+w, y+h), (0,0,255),2)
         starlist_txt = str(px) + "," + str(py) 
         starlist_value = Label(master, text=starlist_txt , bg="gray80")
         starlist_value.grid(row=6+i, column=0)
         starlist_value.extra="starlist"
         draw.point((px, py), 'red')
         starlist_array.append(str(starlist_txt))
   new_image = Image.fromarray(np_new_image)

   displayImage(star_image)


   #displayImage(new_image)

def clear_starlist():
    starlist_array = []
    for label in master.grid_slaves():
       if int(label.grid_info()["row"])>=6:
          print ("removing...")
          label.grid_forget()

def solve_field():
   dataxy = path.replace(".jpg", "-xy.txt")
   fitsxy = path.replace(".jpg", ".xy")
   star_drawing_fn = path.replace(".jpg", "-sd.jpg")
   axy = path.replace(".jpg", ".axy")
   fp = open(dataxy, "w")
   fp.write("x,y\n") 
  

   star_drawing = Image.new('L', (640,360))
   draw = ImageDraw.Draw(star_drawing)

   for star in starlist_array:
      x,y  = star.split(",")
      x1 = int(x)-2
      y1 = int(y)-2
      x2 = int(x)+2
      y2 = int(y)+2
      draw.ellipse((x1, y1, x2, y2), fill=255)
      avg_flux, max_flux = find_flux(int(x), int(y), 10)
      fits_data = str(x) + "," + str(y) + "," + str(avg_flux) + "," + str(max_flux) + "\n"
      fp.write(fits_data)
   fp.close()
   displayImage(star_drawing)
   star_drawing.save(star_drawing_fn)
   ##xyfits = star_data_file.replace(".txt", ".fits")
   #cmd = "/usr/bin/python /usr/local/astrometry/bin/text2fits -f \"ff\" -s \",\" " + dataxy + " " +fitsxy 
   #print (cmd)
   #os.system(cmd)

   cmd = "/usr/local/astrometry/bin/solve-field " + star_drawing_fn + " --overwrite --width=640 --height=360 --scale-units degwidth --scale-low 60 --scale-high 85 --no-remove-lines"
   print (cmd)
   os.system(cmd)

def find_flux(x,y,size):
   box = (x-size,y-size,x+size,y+size)
  
   flux_box = new_image.crop(box) 
   gray_flux_box = flux_box.convert('L')
      
   np_flux_box = np.asarray(gray_flux_box)
   #np_flux_box = cv2.GaussianBlur(np_flux_box, (21, 21), 0)
   avg_flux = np.average(np_flux_box) 
   max_flux = np.amax(np_flux_box)

   return (avg_flux, max_flux)


def motion(event):
   x,y = event.x, event.y
   if image != None and event.widget.extra == "pic":
      box = (x-10,y-10,x+10,y+10)
  
      crop_box = new_image.crop(box) 
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
      xy_value = Label(master, text=xy_val)
      xy_value.grid(row=3, column=1)
      xy_value.extra = "xyv" 
     
      #print ("AXPIX", ax_pixel) 
      displayImageCrop(crop_box)

def mouseClick(event):
   x,y = event.x, event.y
   if event.widget.extra == "pic":
      print("clicked at ", x,y)
      draw = ImageDraw.Draw(new_image)
      draw.point((int(x), int(y)), 'red')
      displayImage(new_image)
   


def OpenImage():
   image = select_image() 
   new_image = image


   if starlist_array != None:
      print("Clear starlist")
      clear_starlist()
   else:
      print ("starlist empty")

   displayImage(image)
   updateContrast(0)


def displayImageCrop(crop_image):
   tkimage = ImageTk.PhotoImage(crop_image)
   imageFrame = Label(image=tkimage)
   imageFrame.image = tkimage
   imageFrame.grid(row=1, column=4, padx=2, pady=2, rowspan=4)
   imageFrame.extra = "pic"

def displayImage(image):
   tkimage = ImageTk.PhotoImage(image)
   imageFrame = Label(image=tkimage, bg="gray80")
   imageFrame.image = tkimage
   imageFrame.grid(row=0, column=0, padx=10, pady=10, columnspan=5)
   imageFrame.extra = "pic"

def OpenVideo():
   print ("BLAH")



# Main window
global master
master = Tk()
master.wm_title("Fireball Camera Manager")

# Menu
menu = Menu(master)
master.config(menu=menu)
master.bind('<Motion>', motion)
#master.bind('<Button-1>', mouseClick)
master.bind("<ButtonPress-1>", ms_create_rect)
master.bind("<ButtonRelease-1>", ms_create_rect)


master.extra="main app"

filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Open Image", command=OpenImage)
filemenu.add_command(label="Open Video", command=OpenVideo)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=master.quit)

brightness_slider = Scale(master, from_=-100, to=100, orient=HORIZONTAL, command=updateBrightness, bg="gray80")
brightness_slider.grid(row=1, column=1, padx=2, pady=2 )
brightness_slider.extra="Brightness Slider"
brightness_label = Label(master, text="Brightness", bg="gray80")
brightness_label.grid(row=1, column=0)
brightness_label.extra="Brightness Label"

contrast_slider = Scale(master, from_=-100, to=100, orient=HORIZONTAL, command=updateContrast, bg="gray80")
contrast_slider.grid(row=2, column=1, padx=2, pady=2 )
contrast_slider.extra="Contrast Slider"
contrast_label = Label(master, text="Contrast", bg="gray80")
contrast_label.grid(row=2, column=0)
brightness_label.extra="Contrast Label"

button = Button(master, text="Find Stars", fg="red", command=detect_all_stars, bg="gray80")
button.grid(row=4, column=0, padx=2, pady=2)
button.extra = "find stars"

button = Button(master, text="Solve Field", fg="red", command=solve_field, bg="gray80")
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




mainloop()

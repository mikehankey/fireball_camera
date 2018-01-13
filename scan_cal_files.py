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
import tkSimpleDialog as tks
import cv2
import glob


def scan_image_for_stars(image_path):
   cal_obj.image = cv2.imread(image_path)
   cal_obj.image = Image.fromarray(cal_obj.image)
   cal_obj.new_image = cal_obj.image

   cal_obj.star_thresh = 7
   cal_obj.find_stars()
   return(len(cal_obj.starlist))

def calibrate_file(image_path):
   cal_obj.image = cv2.imread(image_path)
   cal_obj.image = Image.fromarray(cal_obj.image)
   cal_obj.new_image = cal_obj.image
   cal_obj.star_thresh = 7
   cal_obj.find_stars()

   cal_obj.odds_to_solve = 1000
   cal_obj.code_tolerance = .03
   cal_obj.update_path(image_path)

   cal_obj.solve_field()
   return(cal_obj.solve_success)
   

cal_obj = MFTC.MFTCalibration()
cal_obj.debug = 0

dir = "/var/www/html/out/cal/"
files = glob.glob(dir + "*")
print ("Total files: ", len(files))
print (files)
for file in files:  
   if os.path.isfile(file):
      if "-sd.jpg" in file:
         cmd = "mv " + file + " " + dir + "astrometry/"
         print (cmd)
         os.system(cmd)
      elif ".jpg" in file:
         star_count = scan_image_for_stars(file)
         print (star_count, " Stars found.")
         if star_count == 0: 
            cmd = "mv " + file + " " + dir + "bad/"
            print(cmd)
         elif star_count > 3 and star_count < 100: 
            cmd = "cp " + file + " " + dir + "astrometry/"
            print(cmd)
            os.system(cmd)


            cal_file = file.replace("cal/", "cal/astrometry/") 
            success = calibrate_file(cal_file)
            if success == 1:
               cmd = "mv " + file + " " + dir + "solved/"
               print(cmd)
               os.system(cmd)
            else:
               cmd = "mv " + file + " " + dir + "solve-failed/"
               print(cmd)
               os.system(cmd)

         else: 
            cmd = "mv " + file + " " + dir + "maybe/"
            print(cmd)
            os.system(cmd)
      else: 
         cmd = "mv " + file + " " + dir + "astrometry/"
         print (cmd)
         os.system(cmd)
      

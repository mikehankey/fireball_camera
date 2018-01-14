from amscommon import read_config
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

def characterize_all():
   solves = ('10000', '1000', '100')
   cams = ('1', '2', '3', '4', '5', '6') 
   for solve in solves:
      for cam in cams:
         characterize_cal(cam, solve)

def characterize_cal(cam_num, solved):
   cam_str = "-" + str(cam_num) + ".jpg"
   solve_dir = "solved-" + str(solved) 
   print("/var/www/html/out/cal/solved-" + str(solved) + "/*.jpg")
   images = glob.glob("/var/www/html/out/cal/solved-" + str(solved) + "/*.jpg")
   cmd = "rm /var/www/html/out/cal/solved-" + str(solved) + "/azcenter-" + str(cam_num) + ".txt"
   os.system(cmd)
   print (images)
   for image in images:
      if cam_str in image:
         print (cam_str, image)
         az_file = image.replace(".jpg", "-altaz.txt" )
         az_file = az_file.replace(solve_dir, "astrometry" )
         cmd = "grep CENTER " + az_file + " >> /var/www/html/out/cal/solved-" + str(solved) + "/azcenter-" + str(cam_num) + ".txt"
         print (cmd)
         os.system(cmd) 

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

   # load site and date here...
   config = read_config("conf/config-1.txt")
   cal_obj.loc_lat = config['device_lat']
   cal_obj.loc_lon = config['device_lng']
   cal_obj.loc_alt = config['device_alt']
   cal_obj.cal_time = cal_obj.parse_file_date(image_path)


   cal_obj.odds_to_solve = 10000
   odds = 10000
   cal_obj.code_tolerance = .03
   cal_obj.update_path(image_path)

   cal_obj.solve_field()
   if cal_obj.solve_success == 0:
      odds = 1000
      cal_obj.odds_to_solve = 1000
      cal_obj.solve_field()
      
   if cal_obj.solve_success == 0:
      odds = 100
      cal_obj.odds_to_solve = 100
      cal_obj.solve_field()

   return(cal_obj.solve_success, odds)

   

cal_obj = MFTC.MFTCalibration()
cal_obj.debug = 0

characterize_all()


exit()
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
            success, odds = calibrate_file(cal_file)
            if success == 1:
               cmd = "mv " + file + " " + dir + "solved-" + str(odds) + "/"
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
      

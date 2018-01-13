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

cal_obj = MFTC.MFTCalibration()
cal_obj.debug = 1
matches = cal_obj.find_closest_star_in_catalog(0,0, 51.0644488394, 50.0185282025, 1)

for match in matches:
   print (match)

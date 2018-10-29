#!/usr/bin/python3 

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
from tkinter.filedialog import askopenfilename
import cv2
import CalibrationPage as CP


class AllSky6GUI:
   def __init__(self, parent, *args, **kwargs):

      parent.title("AllSky6 GUI")
      note = ttk.Notebook(parent)
      self.make_tabs(note)


   def make_tabs(self, note):
      tab1 = tk.Frame(note, width=1500, height=900)
      example = CP.CalibrationPage(tab1)
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


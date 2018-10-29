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
import AllSky6GUI as AS6



root = tk.Tk()

AS6.AllSky6GUI(root)
root.mainloop()


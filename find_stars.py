#!/usr/bin/python3

import cv2
import Image

import sys
import os

def find_stars(cal_file):

   cal_image_cv = cv2.imread(cal_file)
   cal_image_pil = Image.fromarray(cal_image_cv)


cal_file = sys.argv[1]

stars = find_stars(cal_file)

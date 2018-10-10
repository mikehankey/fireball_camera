#!/usr/bin/python3 

import sys,os
import glob
from PIL import Image

dir = sys.argv[1]
match_str = sys.argv[2]

size = 384,216 

for infile in sorted((glob.glob(dir + "/*" + match_str))):
   im = Image.open(infile)
   im.thumbnail(size, Image.ANTIALIAS)
   outfile = infile.replace(".jpg", "-thumb.jpg")
   im.save(outfile, "JPEG")



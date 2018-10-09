#!/usr/bin/python3

import sys
import os

file = sys.argv[1]
k_val = sys.argv[2]
k2_val = sys.argv[3]
k3_val = sys.argv[4]
k4_val = sys.argv[5]

outfile = file.replace(".jpg", "-und.jpg")

#cmd = "convert " + file + " -distort barrel '1.0 " + str(-.001) + " 1.0' " + outfile

cmd = "convert " + file + " -distort barrel '" + str(k_val) + " " + str(k2_val) + " " + str(k3_val) + " " + str(k4_val) + "' " + outfile


#cmd = "convert " + file + " -distort Affine '@dist.txt' " + outfile
print(cmd)
os.system(cmd)

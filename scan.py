#!/usr/bin/python3

import os

days = ('2018-03-05', '2018-03-06', '2018-03-07', '2018-03-08', '2018-03-09', '2018-03-10', '2018-03-11', '2018-03-12', '2018-03-13', '2018-03-14', '2018-03-15', '2018-03-16', '2018-03-17', '2018-03-18', '2018-03-19', '2018-03-20', '2018-03-21', '2018-03-22', '2018-03-23', '2018-03-24', '2018-03-25')
cams = ('1', '2', '3', '4', '5', '6') 

for day in days:
   for cam in cams:
      cmd = "./scan-stills2.py " + day + " " + cam
      print(cmd)
      os.system(cmd)
#!/usr/bin/python3

import sys
import os

killer = sys.argv[1]

#cmd = "kill -9 `ps -aux | grep " + killer + " |grep -v grep| awk '{print $2}'`"
cmd = "ps -aux | grep " + killer + " |grep -v grep| awk '{print $2}' > x"
print (cmd)
os.system(cmd)

fp = open("x", "r")
for line in fp:
   pid = line.replace("\n", "")
   cmd = "kill -9 " + pid
   print (cmd)
   os.system(cmd)

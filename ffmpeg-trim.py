#!/usr/bin/python3 

import sys
import os

def ffmpeg_trim (filename, trim_start_sec, dur_sec, out_file_suffix):
   #ffmpeg -i /mnt/ams2/meteors/2018-09-20/2018-09-20_22-20-05-cam5-hd.mp4 -ss 00:00:46 -t 00:00:06 -c copy /mnt/ams2/meteors/2018-09-20/2018-09-20_22-20-05-cam5-hd-trim.mp4

   outfile = filename.replace(".mp4", out_file_suffix + ".mp4")
   cmd = "ffmpeg -i " + filename + " -y -ss 00:00:" + trim_start_sec + " -t 00:00:" + dur_sec + " -c copy " + outfile
   print (cmd)
   os.system(cmd)
   return(outfile)

filename = sys.argv[1]
trim_start_sec = sys.argv[2]
dur_sec = sys.argv[3]
outfile = ffmpeg_trim(filename, trim_start_sec, dur_sec, "-trim")
print(outfile)

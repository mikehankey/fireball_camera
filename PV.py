#!/usr/bin/python3 
import glob
import sys
import ProcessVideo as PV

video_dir = "ffvids/"
arg = sys.argv[1]

if arg == 'batch':
   #do batch for 1 cam
   cam_num = sys.argv[2]
   files = glob.glob(video_dir + cam_num + "/*.mp4")
   for file in sorted(files):
      vid = PV.ProcessVideo()
      vid.orig_video_file = file
      vid.show_video = 1 
      vid.detect_stars = 0 
      vid.detect_motion = 1 
      vid.make_stack = 1 
      #vid.ProcessVideo()
      vid.StackVideo()


else:
   #do 1 file 

   vid = PV.ProcessVideo()
   vid.orig_video_file = arg
   vid.show_video = 1 
   vid.ProcessVideo()

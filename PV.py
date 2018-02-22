#!/usr/bin/python3 
import sys
import ProcessVideo as PV
file = sys.argv[1]

vid = PV.ProcessVideo()
vid.orig_video_file = file
vid.show_video = 0 
vid.ProcessVideo()

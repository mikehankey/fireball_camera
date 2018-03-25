#!/usr/bin/python3
import glob
import sys
import ProcessVideo as PV
import time
import os
import subprocess
import time

#video_dir = "/mnt/ams2/SD"
file = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

vid = PV.ProcessVideo()
vid.orig_video_file = file
vid.show_video = 1
vid.trimVideo(start, end)
#vid.cropVideo(start, end)


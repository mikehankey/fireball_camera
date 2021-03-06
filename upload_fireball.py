#!/usr/bin/python3
import requests
import os
import mimetypes
import sys
import datetime
import time
import settings

from amscommon import read_config

file = sys.argv[1]
video_file = sys.argv[2]
summary_file = sys.argv[3]
motion_frames = sys.argv[4]
cons_motion = sys.argv[5]
color = sys.argv[6]
straight_line = sys.argv[7]
bp_frames = sys.argv[8]
meteor_yn = sys.argv[9]
best_cal = sys.argv[10]

config = read_config()

# UPLOAD LATEST CAM FRAME (every hour)

api_key = config['api_key']
device_id  = config['device_id']
url = settings.API_SERVER + "members/api/cam_api/log_fireball_event"
stat = os.stat(file)
#print (stat)
#datetime = stat.st_birthtime
dt = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
 
# usage: python upload.py type misc_info datetime filename 
# ex: python uploadLatest.py 2016-09-09%2020:03:02 some_info test.jpg

  
#datetime = sys.argv[1]
#misc_info = sys.argv[2]

# The File to send
_file = {'video_file': open(file, 'rb'), 'stack_file': open(stack_file, 'rb'), 'event_summary': open(summary_file, 'rb'}

# The Data to send with the file
_data= { 
   'api_key': api_key, 
   'device_id': device_id, 
   'event_datetime': dt, 
   'format' : 'json'
   'motion_frames': motion_frames,
   'cons_motion':  cons_motion,
   'color':  color,
   'straight_line':  straight_line,
   'bp_frames':  bp_frames,
   'meteor_yn':  meteor_yn,
   'best_calibration':  config['best_caldate'],
}
 
session = requests.Session()
del session.headers['User-Agent']
del session.headers['Accept-Encoding'] 

with requests.Session() as session:
    response = session.post(url, data= _data, files=_file)


print (response.text)
response.raw.close() 

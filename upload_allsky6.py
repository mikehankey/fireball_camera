#!/usr/bin/python3
import requests
import os
import mimetypes
import sys
import datetime
import time
import settings
import platform

from amscommon import read_config

#./upload_allsky6.py /mnt/ams2/SD/proc/2018-03-26/2018-03-26_04-00-03-cam6.mp4 /mnt/ams2/SD/proc/2018-03-26/2018-03-26_04-00-03-cam6-trim-1460.avi /mnt/ams2/SD/proc/2018-03-26/2018-03-26_04-00-03-cam6-stacked.jpg /mnt/ams2/SD/proc/2018-03-26/2018-03-26_04-00-03-cam6-report.txt "2018-03-26 04:01:01" 1

# required params
file = sys.argv[1]
trim_file = sys.argv[2]
stack_file = sys.argv[3]
summary_file = sys.argv[4]
event_datetime = sys.argv[5]
cam_num = sys.argv[6]

config = read_config()

station_id = platform.node()
#config['station_id']
lat = config['device_lat']
lon = config['device_lng']
alt = config['device_alt']

#

# UPLOAD LATEST CAM FRAME (every hour)
api_server = "http://www.allskycams.com"
url = api_server + "/camapi/camapi.php"

# The File to send
_file = {'video_file': open(trim_file, 'rb'), 'video_stack': open(stack_file, 'rb'), 'event_summary': open(summary_file, 'rb')}

# The Data to send with the file
_data= { 
   'station_id': station_id,
   'lat': lat,
   'lon': lon,
   'alt': alt,
   'cam_num': cam_num,
   'event_datetime': event_datetime
}
 
session = requests.Session()
del session.headers['User-Agent']
del session.headers['Accept-Encoding'] 

with requests.Session() as session:
    response = session.post(url, data= _data, files=_file)


print (response.text)
response.raw.close() 

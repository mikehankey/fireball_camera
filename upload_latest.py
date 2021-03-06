#!/usr/bin/python3
import requests
import os
import mimetypes
import sys
import datetime
import time
import settings

from amscommon import read_config


config_file = ""
cam_num = ""

try:
   cam_num = sys.argv[1]
   config_file = "conf/config-" + cam_num + ".txt"
   config = read_config(config_file)
except:
   config = read_config(config_file)
   print (config['cam_ip'])


#config = read_config()

# UPLOAD LATEST CAM FRAME (every hour)

api_key = config['api_key']
device_id  = config['device_id']
url = settings.API_SERVER + "/members/api/cam_api/upload_latest"
file = "/var/www/html/out/latest" + cam_num + ".jpg"
stat = os.stat(file)
#print (stat)
#datetime = stat.st_birthtime
dt = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
 
# usage: python upload.py type misc_info datetime filename 
# ex: python uploadLatest.py 2016-09-09%2020:03:02 some_info test.jpg

  
#datetime = sys.argv[1]
#misc_info = sys.argv[2]

# The File to send
_file = {'file_data': open(file, 'rb')}

# The Data to send with the file
_data= {'api_key': api_key, 'device_id': device_id, 'datetime': dt, 'format' : 'json'}
 
session = requests.Session()
del session.headers['User-Agent']
del session.headers['Accept-Encoding'] 

with requests.Session() as session:
    response = session.post(url, data= _data, files=_file)


print (response.text)
response.raw.close() 

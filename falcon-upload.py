#!/usr/bin/python3 

import requests
import os
import mimetypes
import sys
import datetime
import time
import json

json_data = open("conf/config.json").read()
device_data = json.loads(json_data)
device_id = device_data['device_id']
mac_addr = device_data['mac_addr']

api_host = "http://nodes.allskycams.com:8000/"
api_url = api_host + "upload_media"

# The File to send
image_filename = "2018-10-10_10-10-10-cam1-stacked.jpg"


multipart_form_data = {
   'media_file' : (image_filename, open(image_filename, 'rb')),
   'device_id' : device_id,
   'mac_addr' : mac_addr ,
   'media_type' : 'image' ,
   'upload_type' : 'clip_stack' 
}

response = requests.post(api_url, files=multipart_form_data)






print (response.text)
print (response)
response.raw.close()


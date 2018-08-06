#!/usr/bin/python3
# amsaware
# This script checks for AMS Fireball events and reports and
# checks the recordings of this device to see if the event was
# capture. If video files exist around the time of the event
# the files will be uploaded to the AMS for further analysis.
import settings
import sys
import os
import time as gtime
from os import listdir
from os.path import isfile, join
import json, requests
import numpy as np
from datetime import datetime, date, time
from dateutil import parser

def get_events(myyear, min_reports):

   api_key = "QwCsPJKr87y15Sy"
   url = settings.API_SERVER + "members/api/open_api/get_events"
   data = {'api_key' : api_key, 'year' : myyear, 'min_reports' : min_reports, 'format' : 'json'}
#, format' : 'json'}
   r = requests.get(url, params=data)
   my_data = r.json()
   for key in my_data['result']:
      key = key.replace("Event #", "")
      key = key.replace("\n", "")
      (y,e) = key.split("-")
      print (y,e)

get_events(2017, 5)

#!/usr/bin/python3

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
from amscommon import read_config
#from math import radians, cos, sin, asin, sqrt
from math import * 

def check_capture (cap_dir, captures, event_datetime):
   event_datetime = parser.parse(event_datetime)
   for capture in captures:
      if "avi" in capture:
         (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(cap_dir + capture)
         file_date = datetime.strptime(gtime.ctime(ctime), "%a %b %d %H:%M:%S %Y")
         time_diff = event_datetime - file_date
         minutes, seconds = divmod(time_diff.total_seconds(), 60)
         if minutes > -180 and minutes < 180:
            print ("\tPossible capture " + capture);
            print ("\t", minutes, capture, event_datetime , gtime.ctime(ctime))


def read_files(dir):
    captures = [f for f in listdir(dir) if isfile(join(dir, f))]
    return(captures)

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    bearing = atan2(sin(lon2-lon1)*cos(lat2), cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1))
    bearing = degrees(bearing)
    bearing = (bearing + 360) % 360
    return km, bearing

def get_ams_event(year, event_id, ratings):
   num_reports = 0
   api_key = "QwCsPJKr87y15Sy"
   url = settings.API_SERVER + "/members/api/open_api/get_event"
   data = {'api_key' : api_key, 'year' : year, 'event_id' : event_id, 'format' : 'json', 'ratings': ratings, 'override': 0}
   r = requests.get(url, params=data)
   my_data = r.json()
   if "result" not in my_data.keys():
      #print ("No trajectory for this event.", event_id)
      return(0,0,0,0,0,0)
   #try:
   #   event_datetime_utc = my_data['result'][event_key]['avg_date_utc']
   #except:
   #   print ("No trajectory for this event.")
   #   return(0)

   event_key = "Event #" + str(event_id) + "-" + str(year)
   event_datetime_utc = my_data['result'][event_key]['avg_date_utc']
   fb_start_lat =  my_data['result'][event_key]['start_lat']
   fb_start_lon =  my_data['result'][event_key]['start_long']
   fb_start_alt =  my_data['result'][event_key]['start_alt']
   fb_end_lat =  my_data['result'][event_key]['end_lat']
   fb_end_lon =  my_data['result'][event_key]['end_long']
   fb_end_alt =  my_data['result'][event_key]['end_alt']
   impact_lat = my_data['result'][event_key]['impact_lat'];
   impact_lon = my_data['result'][event_key]['impact_long']
   #(num_reports, xxx) =my_data['result'][event_key]['num_reports_for_options'].split("/")
   #print (my_data['result'][event_key]['num_reports_for_options'])
   epicenter_lon = my_data['result'][event_key]['epicenter_long']
   epicenter_lat = my_data['result'][event_key]['epicenter_lat']

   # REFINE THE DATE
   epc_distance,epc_bearing = haversine(float(config['device_lng']), float(config['device_lat']), epicenter_lon, epicenter_lat)
   sp_distance,sp_bearing = haversine(float(config['device_lng']), float(config['device_lat']), fb_start_lon , fb_start_lat)
   ep_distance,ep_bearing = haversine(float(config['device_lng']), float(config['device_lat']), fb_end_lon , fb_end_lat)


   return(event_id, event_datetime_utc, int(sp_distance), int(sp_bearing), int(ep_distance), int(ep_bearing));






def get_close_events(start_date, end_date, lat, lon):
   err = 1
   events = set()
   event_dates = {}
   event_counts = {}
   event_data = {}
   api_key = "QwCsPJKr87y15Sy"
   url = settings.API_SERVER + "members/api/open_api/get_close_reports"
   data = {'api_key' : api_key, 'start_date' : start_date, 'end_date' : end_date, 'lat': lat, 'lng': lon, 'format' : 'json'}
   #print (data)
   r = requests.get(url, params=data)
   my_data = r.json()
#   print (my_data);
   try: 
      print (my_data['errors'])
   except: 
      print ("No errors.");
      err = 0

   if err == 1:
      exit() 

   for row in my_data['result']:
       #print (str(row), str(my_data['result'][row]['latitude']), str(my_data['result'][row]['longitude']), str(my_data['result'][row]['report_date_utc']))
       if "#" in str(row):
           (a, b, c) = str(row).split(" ")
           (utc_date) = my_data['result'][row]['report_date_utc']
           (event_id, year) = b.split("-", 2)
           event_id = event_id.replace("#", "")
           event_id = int(event_id)
           events.add(event_id)
           event_dates[event_id] = utc_date
           try: 
              event_counts[event_id] += 1 
           except:  
              event_counts[event_id] = 1 
       else:
           print ("skip pending report")

   false_captures = read_files("/var/www/html/out/false")
   maybe_captures = read_files("/var/www/html/out/maybe")
   
   for event_id in events:
      if event_counts[event_id] > 1:
         #print (event_id, event_dates[event_id], event_counts[event_id])
         event_data = get_ams_event('2017', event_id, 1)
         if event_data[0] != 0 and ((event_data[2] <= 180 or event_data[4] <= 180) and (event_data[2] < 1000 and event_data[4] < 1000)):
            print(event_data)
            check_capture("/var/www/html/out/false/", false_captures, event_data[1])  
            check_capture("/var/www/html/out/maybe/", maybe_captures, event_data[1])  
         

#start_date = sys.argv[1]
#end_date = start_date + " 23:59:59"
#start_date = start_date + " 00:00:00"

start_date = '2017-07-01'
end_date = '2017-11-01'

config = read_config();
get_close_events(start_date, end_date, config['device_lat'], config['device_lng'])



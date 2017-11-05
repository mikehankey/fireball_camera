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
      print ("No trajectory for this event.", event_id)
      return(0)
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
   #type = 'datetime'
   #dates = get_ams_reports(year, event_id, type, ratings)
   #if len(dates) > 0:
   #   better_event_datetime =  avg_dates(event_datetime_utc, dates)
   epc_distance,epc_bearing = haversine(float(config['device_lng']), float(config['device_lat']), epicenter_lon, epicenter_lat)
   sp_distance,sp_bearing = haversine(float(config['device_lng']), float(config['device_lat']), fb_start_lon , fb_start_lat)
   ep_distance,ep_bearing = haversine(float(config['device_lng']), float(config['device_lat']), fb_end_lon , fb_end_lat)

   # PRINT EVENT DETAILS
   if (sp_distance < 200 or ep_distance < 200) and (sp_distance < 1000 and ep_distance < 1000):
      print ("Event ID: \t" + str(event_id))
      print ("Average Event Datetime: \t" + event_datetime_utc)
      print ("Event Epicenter Lat/Lon:\t" + str(epicenter_lat) + "/" + str(epicenter_lon))

      print ("Epicenter Distance:", epc_distance)
      print ("Epicenter Bearing:", epc_bearing)

      print ("Start Point Distance:", sp_distance)
      print ("Start Point Bearing:", sp_bearing)

      print ("End Point Distance:", ep_distance)
      print ("End Point Bearing:", ep_bearing)
      print ("------")


   #if fb_start_lat >= min_lat and fb_start_lat <= max_lat:
   #    start_lat_match = 1
   #else:
   #    start_lat_match = 0
   #if fb_start_lon >= min_lon and fb_start_lon <= max_lon:
   #    start_lon_match = 1
   #else:
   #    start_lon_match = 0

#   if fb_end_lat >= min_lat and fb_end_lat <= max_lat:
#       end_lat_match = 1
#   else:
#       end_lat_match = 0
#   if fb_end_lon >= min_lon and fb_end_lon <= max_lon:
#       end_lon_match = 1
#   else:
#       end_lon_match = 0

#   print ("Start Point in FOV:\t\t", start_lat_match, start_lon_match)
#   print ("End Point in FOV:\t\t", end_lat_match, end_lon_match)
   #return(better_event_datetime)





def get_close_events(start_date, end_date, lat, lon):
   err = 1
   events = set()
   event_dates = {}
   event_counts = {}
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
   
   for event_id in events:
      if event_counts[event_id] > 1:
         #print (event_id, event_dates[event_id], event_counts[event_id])
         get_ams_event('2017', event_id, 1)
         

start_date = sys.argv[1]
end_date = start_date + " 23:59:59"
start_date = start_date + " 00:00:00"

start_date = '2017-07-01'
end_date = '2017-11-01'

config = read_config();
get_close_events(start_date, end_date, config['device_lat'], config['device_lng'])



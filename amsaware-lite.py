#!/usr/bin/python3
import requests
import settings
import sys
import datetime
from datetime import timedelta
from amscommon import read_config
import glob
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


def parse_file_date(file_name):
   el = file_name.split("/")
   file_name = el[-1]

   year = file_name[0:4]
   month = file_name[4:6]
   day = file_name[6:8]
   hour = file_name[8:10]
   min = file_name[10:12]
   sec = file_name[12:14]
   #date_str = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec
   date_str = year + "/" + month + "/" + day + " " + hour + ":" + min + ":" + sec
   mydate = datetime.datetime(int(year), int(month), int(day), int(hour), int(min), int(sec))
   return(mydate)

def get_close_events(start_date, end_date, lat, lon):

   events = set()
   event_dates = {}
   api_key = "QwCsPJKr87y15Sy"
   url = settings.API_SERVER + "members/api/open_api/get_close_reports"
   data = {'api_key' : api_key, 'start_date' : start_date, 'end_date' : end_date, 'lat': lat, 'lng': lon, 'format' : 'json', 'distance' : '100'}
   #print (data)
   r = requests.get(url, params=data)
   my_data = r.json()
   #print my_data

   if "result" not in my_data.keys():
      print ("No close events for:" +  start_date)
      return(0)


   count = 0
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
           #print (row)
           count = count + 1
           print ("EVENT: ", event_id)
       else:
           #print (row)
           #print ("pending report")
           count = count + 1

   (sd, ed) = get_ams_event_distance(year, event_id, lat, lon)
   print ("Distance:", sd, ed)

   if sd < 300 or ed < 300:
      return(1)
   else:
      return(0)
 

def get_ams_event_distance(year, event_id, lat,lon):
   num_reports = 0
   api_key = "QwCsPJKr87y15Sy"
   url = settings.API_SERVER + "/members/api/open_api/get_event"
   data = {'api_key' : api_key, 'year' : year, 'event_id' : event_id, 'format' : 'json', 'ratings': 0, 'override': 0}
   r = requests.get(url, params=data)
   my_data = r.json()
   if "result" not in my_data.keys():
      print ("No trajectory for this event.")
      return(1000,1000)
   try:
      event_datetime_utc = my_data['result'][event_key]['avg_date_utc']
   except:
      print ("No trajectory for this event.")
      return(1000,1000)

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
   epicenter_lon = my_data['result'][event_key]['epicenter_long']
   epicenter_lat = my_data['result'][event_key]['epicenter_lat']

   distance_start = haversine(float(lat),float(lon), float(fb_start_lat), float(fb_start_lon))
   distance_end = haversine(float(lat),float(lon), float(fb_end_lat), float(fb_end_lon))
   return(distance_start, distance_end)


#file = sys.argv[1]
config = read_config()

files = glob.glob("/var/www/html/out/false/night/*.avi")

for file in files:
   file_date = parse_file_date(file)
   xx = file.split("/")
   fn = xx[-1]
   dir = file.replace(fn, "")
   start_date = file_date - timedelta(hours=1)
   end_date = file_date + timedelta(hours=1)
   #print (file_date, start_date, end_date)

   match = get_close_events(str(start_date), str(end_date), config['device_lat'], config['device_lng'])
   # if close reports exist, get the event detail and see if it is within acceptable distance. 
   if match == 1:
      new_dir = dir + "events"
   else:
      new_dir = dir + "noevents"
   cmd = "mv " + file + " " + new_dir
   print (cmd)

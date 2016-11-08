# amsaware
# This script checks for AMS Fireball events and reports and 
# checks the recordings of this device to see if the event was 
# capture. If video files exist around the time of the event
# the files will be uploaded to the AMS for further analysis. 

import json, requests
import numpy as np
from datetime import datetime, date, time
from dateutil import parser

def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
    return(config)


def get_ams_reports(ams_year, ams_event_id,type, ratings):
   ams_api_key = "QwCsPJKr87y15Sy"
   url = "http://www.amsmeteors.org/members/api/open_api/get_reports_for_event"
   data = {'api_key' : ams_api_key, 'year' : ams_year, 'event_id' : ams_event_id, 'format' : 'json', 'override' : 0, 'ratings' : ratings}
   r = requests.get(url, params=data)
   dates = []
   my_data = r.json()
   data = json.loads(r.text)
   #print data
   for key in data['result']:
      ams_witness_id = data['result'][key]['report_id']
      dt = data['result'][key]['report_date_utc']
      record_date = data['result'][key]['report_date_utc']
      lat = data['result'][key]['latitude']
      lon = data['result'][key]['longitude']
      alt = data['result'][key]['altitude']
      az1 = data['result'][key]['initial_azimuth']
      el1 = data['result'][key]['initial_altitude']
      az2 = data['result'][key]['final_azimuth']
      el2 = data['result'][key]['final_altitude']
      wr = data['result'][key]['rating']
      if type == 'detail':
         if wr >= ratings:
            print (ams_witness_id + "|" + dt + "|" + record_date + "|" + lat + "|" + lon + "|" + alt + "|" + az1 + "|" + el1 + "|" + az2 + "|" + el2 + "|")
      dates.append(dt)

   if (type == 'datetime'):
      return(dates)

def avg_dates (avg_date_utc, datetimes):
   good_datetimes = []
   good_avg_date = parser.parse(avg_date_utc)
   for dts in datetimes:
      dt = parser.parse(dts)
      time_diff = dt - good_avg_date
      minutes, seconds = divmod(time_diff.total_seconds(), 60)
      if minutes < 20 and minutes > -20:
         good_datetimes.append(dt)

   avg_date = datetime.date(good_avg_date)

   total = sum(dt.hour * 3600 + dt.minute * 60 + dt.second for dt in good_datetimes)
   avg = total / len(datetimes)
   minutes, seconds = divmod(int(avg), 60)
   hours, minutes = divmod(minutes, 60)
   return datetime.combine(date(avg_date.year, avg_date.month, avg_date.day), time(hours, minutes, seconds))

def get_ams_event(year, event_id, ratings):
   num_reports = 0
   ams_api_key = "QwCsPJKr87y15Sy"
   url = "http://www.amsmeteors.org/members/api/open_api/get_event"
   data = {'api_key' : ams_api_key, 'year' : year, 'event_id' : event_id, 'format' : 'json', 'ratings': ratings, 'override': 0}
   r = requests.get(url, params=data)
   my_data = r.json()

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
   (num_reports, xxx) =my_data['result'][event_key]['num_reports_for_options'].split("/")
   epicenter_lon = my_data['result'][event_key]['epicenter_long']
   epicenter_lat = my_data['result'][event_key]['epicenter_lat']

   # REFINE THE DATE
   type = 'datetime'
   dates = []
   dates = get_ams_reports(year, event_id, type, ratings)
   if len(dates) > 0:
      better_event_datetime =  avg_dates(event_datetime_utc, dates)

   # PRINT EVENT DETAILS
   print ("Average Event Datetime: \t" + event_datetime_utc)
   if len(dates) > 0:
      print ("Better Average Datetime:\t" + better_event_datetime.strftime("%Y-%m-%d %H:%M:%S"))
   print ("Fireball Start Lat/Lon/Alt:\t" + str(fb_start_lat) + "/" + str(fb_start_lon) + "/" + str(fb_start_alt))
   print ("Fireball End Lat/Lon/Alt:\t" + str(fb_end_lat) + "/" + str(fb_end_lon) + "/" + str(fb_end_alt))
   print ("Impact Lat/Lon/Alt:      \t" + str(impact_lat) + "/" + str(impact_lon) + "/0")
   print ("Event Epicenter Lat/Lon:\t" + str(epicenter_lat) + "/" + str(epicenter_lon))

def get_close_events(start_date, end_date, lat, lon):

   events = set() 
   ams_api_key = "QwCsPJKr87y15Sy"
   url = "http://www.amsmeteors.org/members/api/open_api/get_close_reports"
   data = {'api_key' : ams_api_key, 'start_date' : start_date, 'end_date' : end_date, 'lat': lat, 'lng': lon, 'format' : 'json'}
   r = requests.get(url, params=data)
   my_data = r.json()
   #print my_data
   for row in my_data['result']:
       #print (str(row), str(my_data['result'][row]['latitude']), str(my_data['result'][row]['longitude']), str(my_data['result'][row]['report_date_utc']))
       if "#" in str(row):
           (a, b, c) = str(row).split(" ")
           (event_id, year) = b.split("-", 2)
           event_id = event_id.replace("#", "")
           event_id = int(event_id)
           events.add(event_id)
       else: 
           print ("skip pending report")   

   print ("Unique events within your area.")
   for event_id in events:
       print ("Event ID:\t\t\t" + str(event_id))
       get_ams_event(year, event_id, 1)



get_close_events('2016-11-07', '2016-11-08', 39, -76)

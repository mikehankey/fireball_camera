#!/usr/bin/python3
import requests
import settings
import sys
import datetime
from datetime import timedelta
from amscommon import read_config
import glob

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
   data = {'api_key' : api_key, 'start_date' : start_date, 'end_date' : end_date, 'lat': lat, 'lng': lon, 'format' : 'json'}
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
       else:
           #print (row)
           #print ("pending report")
           count = count + 1

   return(count)


#file = sys.argv[1]
config = read_config()

files = glob.glob("/var/www/html/out/false/night/*.avi")

for file in files:
   file_date = parse_file_date(file)
   start_date = file_date - timedelta(hours=1)
   end_date = file_date + timedelta(hours=1)
   print (file_date, start_date, end_date)

   count = get_close_events(str(start_date), str(end_date), config['device_lat'], config['device_lng'])
   print (count, "Close events")

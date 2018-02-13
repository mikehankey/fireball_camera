#!/usr/bin/python3
#this script sets up the cameras default params
# important backdoor URLS
# OSD - /videoosd.asp?
# Settings - /videolens.asp

import datetime
import sys
import requests
from amscommon import read_config

config_file = ""

try:
   cam_num = sys.argv[1]
   config_file = "conf/config-" + cam_num + ".txt"
   config = read_config(config_file)
   print ("reading... ", config_file)
except:
   config = read_config(config_file)
   print ("reading default... ", config_file)


print (config)

#config = read_config()

cam_ip = config['cam_ip']

cur_datetime = datetime.datetime.now()
req_str = "year=" + str(cur_datetime.strftime("%Y")) + "&" + "month=" + str(cur_datetime.strftime("%m")) + "&" + "day=" + str(cur_datetime.strftime("%d")) + "&" + "hour=" + str(cur_datetime.strftime("%H")) + "&" + "minute=" + str(cur_datetime.strftime("%M")) + "&" + "second=" + str(cur_datetime.strftime("%S"))


print ("Set timezone and NTP server.")
url = "http://" + str(cam_ip) + "/cgi-bin/date_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&timezone=14&ntpHost=clock.isc.org"
print (url)
r = requests.get(url)
print (r.text)

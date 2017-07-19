#!/usr/bin/python3
#this script sets up the cameras default params
# important backdoor URLS
# OSD - /videoosd.asp?
# Settings - /videolens.asp


import requests
from amscommon import read_config

config = read_config()

cam_ip = config['cam_ip']

print ("Setting up defaults for camera on IP address:", cam_ip)

print ("Set timezone and NTP server.")
url = "http://" + str(cam_ip) + "/cgi-bin/date_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&timezone=14&ntpHost=clock.isc.org"
print (url)
r = requests.get(url)
print (r.text)

#!/usr/bin/python3
import requests, json
import sys
import netifaces
from amscommon import read_config
config = read_config()

new_install = 0

# check to see if this is a new install.
try: 
   api_key = config['ams_api_key']
except:
   new_install = 1
try: 
   cam_id = config['ams_api_key']
except:
   new_install = 1

# cam id or API key don't exist. 

# register device with AMS
eth0_mac = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
wlan0_mac = netifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0]['addr']

try:
    eth0_ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
except:
    eth0_ip = "0.0.0.0"
try:
    wlan0_ip= netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
except:
    wlan0_ip = "0.0.0.0"

print ("ETH0 MAC: ", eth0_mac)
print ("WLAN MAC: ", wlan0_mac)
print ("ETH0 IP: ", eth0_ip)
print ("WLAN IP: ", wlan0_ip)

r = requests.get('http://www.amsmeteors.org/members/api/cam_api/mkdevice?format=json&LAN_MAC=' + eth0_mac + '&WLAN_MAC=' + wlan0_mac)
#print (r.text)
fp = open("register.txt", "w")
fp.write(r.text)
fp.close()

# GET THE DEVICE INFO

r = requests.get('http://www.amsmeteors.org/members/api/cam_api/get_device_info?format=json&LAN_MAC=' + eth0_mac + '&WLAN_MAC=' + wlan0_mac)
#print (r.text)
fp = open("device_info.txt", "w")
fp.write(r.text)
fp.close()

data = json.loads(r.text)
print (data)
print ("Cam ID: ", data['result'][0]['cam_id'])
exit()

for key in data['result']:
   print ("Cam ID: ", key['cam_id'])
   print ("Cam IP: ", key['cam_ip'])
   print ("Heading: ", key['heading'])
   print ("Cam Lat: ", key['cam_lat'])
   print ("Cam Lon: ", key['cam_lng'])
   print ("Cam Elv: ", key['cam_elv'])
   #print ("Cam Alt: ", key['cam_alt'])

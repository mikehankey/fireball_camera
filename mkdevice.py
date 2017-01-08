#!/usr/bin/python3
import requests, json
import sys
import netifaces
from amscommon import read_config
config = read_config()

new_install = 0

# check to see if this is a new install.
try: 
   api_key = config['api_key']
except:
   new_install = 1
try: 
   device_id = config['device_id']
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
print ("Device ID: ", data['result'][0]['device_id'])
exit()

for key in data['result']:
   print ("Cam ID: ", key['device_id'])
   print ("Cam IP: ", key['cam_ip'])
   print ("Heading: ", key['heading'])
   print ("Device Lat: ", key['device_lat'])
   print ("Device Lon: ", key['device_lng'])
   print ("Device Elv: ", key['device_elv'])

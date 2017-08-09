#!/usr/bin/python3
import requests, json
import sys
import netifaces
import os
import os.path 
import settings
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './config')))
from config_func import add_to_config, read_config, get_device_info_and_config
 

output = ""

# Test if config exists - create it if it doesnt
# (this way we don't have to create the config file manually)
if(os.path.isfile('config.txt')):
  config = read_config()
  output = output + os.linesep +  'WARNING: config.txt already exists'
else:
  open('config.txt', 'a')
  output = output + os.linesep +  'CREATION of config.txt'
  
# Get info to Register new device with AMS
eth0_mac  = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
wlan0_mac = netifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0]['addr']

try:
    eth0_ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
except:
    eth0_ip = "0.0.0.0"
try:
    wlan0_ip= netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
except:
    wlan0_ip = "0.0.0.0"
 

output = output + os.linesep +  "Device/Network Info"
output = output + os.linesep +  "ETH0 MAC: " + eth0_mac
output = output + os.linesep +  "WLAN MAC: " +  wlan0_mac
output = output + os.linesep +  "ETH0 IP (LAN IP): " + eth0_ip
output = output + os.linesep +  "WLAN IP: " + wlan0_ip

try:
   r = requests.get(settings.API_SERVER + 'members/api/cam_api/mkdevice?format=json&LAN_MAC=' + eth0_mac + '&WLAN_MAC=' + wlan0_mac + '&lan_ip=' + eth0_ip + 'wlan_ip=' + wlan0_ip)
   fp = open("register.txt", "w+")
   fp.write(r.text)
   fp.close()
except:
   output = output + os.linesep +  "mknewdevice failed"


data = json.loads(r.text)
try:
   if data['errors']['Invalid_data'] == 'LAN_MAC WLAN_MAC combination must be unique.':
      output = output + os.linesep +  "Device already exist!" 
   else:
      output = output + os.linesep +  "Device created." 
except:
   output = output + os.linesep +  "Device Created."
  
#LOG IP OF DEVICE. 
msg = "lan_ip=" + eth0_ip + ":wlan_ip=" + wlan0_ip
r = requests.post(settings.API_SERVER + 'members/api/cam_api/addLog', data={'LAN_MAC': eth0_mac, 'WLAN_MAC': wlan0_mac, 'msg': msg})

res = r.text
x, id = res.split("device_id: ")

hostname = "ams" + id.rstrip("\n") 
out = open("/home/pi/fireball_camera/host", "w+") 
out.write(hostname)
out.close()
os.system("sudo cp /home/pi/fireball_camera/host /etc/hostname")


output = output + os.linesep +  'Hostname updated:'+ " ams" + id.rstrip("\n")

# Here we populate the config file with the info we got (and we need...)
add_to_config('lan_ip',eth0_ip) 
add_to_config('device_id',id.rstrip("\n"))
add_to_config('hd',0)
add_to_config('wlan_ip',wlan0_ip)
add_to_config('wlan_mac',wlan0_mac)
add_to_config('lan_mac',eth0_mac) 

i = datetime.now()
add_to_config('reg_date',i.strftime('%Y-%m-%d %H:%M:%S')) 
p = read_config();

output = output + os.linesep +  "Config file updated."

# Get Info from the API in case the cam already has info in the database
# update the config file accordingly 
get_device_info_and_config()

print(output)
#!/usr/bin/python3
import requests, json
import sys
import netifaces
import os
import settings
from amscommon import read_config, write_config, put_device_info
from collections import defaultdict

def get_cam_mac(config):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/sysparam_cgi?user=admin&pwd="+ config['cam_pwd']
   print (url)
   r = requests.get(url)
   lines = r.text.split("\n")
   for line in lines:
      if "MACAddress" in line:
         line = line.replace("<MACAddress>", "") 
         line = line.replace("</MACAddress>", "") 
         cam_mac = line.replace("\t", "") 

   return(cam_mac)

config_file = ""
cam_num = ""

try:
   cam_num = sys.argv[1]
   config_file = "conf/config-" + cam_num + ".txt"
   config = read_config(config_file)
except:
   config = read_config(config_file)

   print (config['cam_ip'])

cam_mac = get_cam_mac(config)
print (cam_mac)



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
# enp1s0

try: 
   enp1s0_mac = netifaces.ifaddresses('enp1s0')[netifaces.AF_LINK][0]['addr']
   wlan0_mac = netifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0]['addr']
except: 
   enp1s0_mac = netifaces.ifaddresses('enp1s0')[netifaces.AF_LINK][0]['addr']
   wlan0_mac = cam_mac


try:
    enp1s0_ip = netifaces.ifaddresses('enp1s0')[netifaces.AF_INET][0]['addr']
except:
    enp1s0_ip = "0.0.0.0"
try:
    wlan0_ip= netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
except:
    wlan0_ip = "0.0.0.0"

print ("ETH0 MAC: ", enp1s0_mac)
print ("WLAN MAC: ", wlan0_mac)
print ("ETH0 IP: ", enp1s0_ip)
print ("WLAN IP: ", wlan0_ip)

try:
   r = requests.get(settings.API_SERVER + 'members/api/cam_api/mkdevice?format=json&LAN_MAC=' + enp1s0_mac + '&WLAN_MAC=' + wlan0_mac + '&lan_ip=' + enp1s0_ip + '&wlan_ip=' + config['cam_ip'])
   fp = open("register.txt", "w")
   fp.write(r.text)
   fp.close()
except:
   print ("mkdevice failed.")

data = json.loads(r.text)
try:
   if data['errors']['Invalid_data'] == 'LAN_MAC WLAN_MAC combination must be unique.':
      print ("Device already created.")
   else:
      print ("Device created.")
except:
   print ("Device Created.")

print (config)
  
#LOG IP OF DEVICE. 
msg = "lan_ip=" + enp1s0_ip + ":wlan_ip=" + config['cam_ip'] 
r = requests.post(settings.API_SERVER + 'members/api/cam_api/addLog', data={'LAN_MAC': enp1s0_mac, 'WLAN_MAC': wlan0_mac, 'msg': msg})

res = r.text

x, id = res.split("device_id: ")

hostname = "ams" + id.rstrip("\n")
print ("ID: ", hostname)
out = open("/home/pi/fireball_camera/host", "w") 
out.write(hostname)
out.close()
#os.system("sudo cp /home/pi/fireball_camera/host /etc/hostname")

#exit()

# GET THE DEVICE INFO

r = requests.get(settings.API_SERVER + 'members/api/cam_api/get_device_info?format=json&LAN_MAC=' + enp1s0_mac + '&WLAN_MAC=' + wlan0_mac)
#print (r.text)
fp = open("device_info.txt", "w")
fp.write(r.text)
fp.close()
print (r.text)  

data = json.loads(r.text)
for key in data['result'][1]:
   print (key)

  

#try:
if 1 == 1: 
   for key in data['result'][1]:
      print (key)

   dev_data = data['result'][0]['cam'][0]
   operator_data = data['result'][1]['operator'][0]
   for key in operator_data:
      if type(operator_data[key]) is str:
         print (key, operator_data[key])
         config[key]=operator_data[key]

   try:
      if config['cam_ip'] == '':
         print ("Cam id is null");
   except: 
      config['cam_ip'] = '192.168.1.88';

   for key in dev_data:
      if type(dev_data[key]) is str and key != 'cam_ip' and key != 'IP':
         print (key, dev_data[key])
         config[key]=dev_data[key]
   write_config(config, config_file)
   put_device_info(config)
#except: 
#   print ("Device is not claimed yet or lat long not setup.")



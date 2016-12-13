import requests
import sys
import netifaces

#intf = netifaces.interfaces()

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


# usage: python logger.py type msg
# type = type of log message (reboot, system, capture, calibration) 
# msg = log message 
print ("ETH0 MAC: ", eth0_mac)
print ("WLAN MAC: ", wlan0_mac)
print ("ETH0 IP: ", eth0_ip)
print ("WLAN IP: ", wlan0_ip)

url = 'http://www.amsmeteors.org/members/api/cam_api/mkdevice?LAN_MAC=' + eth0_mac + '&WLAN_MAC=' + wlan0_mac
print (url)
r = requests.post('http://www.amsmeteors.org/members/api/cam_api/mkdevice?LAN_MAC=' + eth0_mac + '&WLAN_MAC=' + wlan0_mac)
print (r.text)

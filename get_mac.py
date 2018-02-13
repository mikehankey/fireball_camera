import sys
import time
import os
import requests


def get_mac (cam_ip, cam_owner, cam_id):
   # get the mac address
   file = open("caminfo/" + str(cam_owner) + ".txt", "a")
   url = "http://" + str(cam_ip) + "/cgi-bin/sysparam_cgi?user=admin&pwd=admin"
   print (url)
   r = requests.get(url)
   lines = r.text.split("\n")
   for line in lines:
      if "MACAddress" in line:
         file.write(str(cam_id) +"|");
         line = line.replace("\t", "");
         line = line.replace("<MACAddress>", "");
         line = line.replace("</MACAddress>", "");
         file.write(line)
         file.write("\n")

ip = sys.argv[1]
cam_owner = sys.argv[2]
cam_id = sys.argv[3]

get_mac(ip, cam_owner, cam_id)

#!/usr/bin/python3
from collections import defaultdict
#from random import *
import random
import glob
import subprocess
import cgi
import cgitb
import os
video_dir = "/mnt/ams2/SD/"
from pathlib import Path

#cgi.enable()
print ("Content-type: text/html\n\n")



def ping_cam(ip):
   cmd = "ping -c 1 " + ip + " > /dev/null"
   #output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   response = os.system(cmd)
   if response == 0:
      print ("Cam found on!" + ip)
      return(1)

def scan_network():
   ip_range = "192.168.176."
   for i in range(70,80):
      ip = ip_range + str(i)
      ping_cam(ip)
      print("<BR>")




def main():
   form = cgi.FieldStorage()
   act = form.getvalue('act')
   act = "scan_network"
   print ("<h1>Camera DNS Setup</h1>")
   print ("Functions <UL>")
   print ("<li><a href=setup-dhcp.py?act=view_dhcp_conf>View DHCP config file</a></li>")
   print ("<li><a href=setup-dhcp.py?act=scan_network>Scan network for cameras</a></li>")
   if act == 'view_dhcp_conf':
      view_dhcp_conf()
   if act == 'scan_network':
      scan_network()
   
def view_dhcp_conf():
   cmd = "cat /etc/dhcp/dhcpd.conf"
   output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   print ("<PRE>")
   print(output)
   print ("</PRE>")

main()

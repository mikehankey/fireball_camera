#!/usr/bin/python3
import glob
import subprocess 
import cgi
import cgitb
import os
import netifaces

video_dir = "/mnt/ams2/SD/"





def header():
   print ("Content-type: text/html\n\n")
   print ("<h1>AllSky6 Setup</h1>")

def menu():
   header()
   print("<UL>")
   print("<LI><a href=setup.py?act=change_network_settings>Change Network Settings</a>")
   print("<LI><a href=setup.py?act=find_factory_cameras>Find Cameras with Factory Settings</a>")

def main():
   form = cgi.FieldStorage()
   act = form.getvalue('act')
   act = 'change_network_settings'
   if act == 'change_network_settings':
      change_network_settings()
   else:
      menu()

def change_network_settings():
   header()
   print ("<h2>Change Network Settings</h2>")
   print ("<P>This menu option should only be used if you are setting up from a kit and this is the first time you are turning on the camera module.</P>")
   ifaces = netifaces.interfaces()   
   print("<PRE>IFACES:", ifaces, "\n")
   ifc = 0
   int_text = []
   for iface in ifaces:
      if iface != 'lo' and iface[0] != 'w':
         iface_info = netifaces.ifaddresses(iface)
         #print (iface, iface_info[netifaces.AF_INET])
         ip = iface_info[netifaces.AF_INET][0]['addr']
         broadcast  = iface_info[netifaces.AF_INET][0]['broadcast']
         network = broadcast.replace('255', '0')
         #print (iface, ip, broadcast, network, "\n")
         text = make_interface(iface, 0, ip, broadcast, network)
         print (text)
         ifc = ifc + 1 


def make_interface(eth, dhcp, ip, broadcast, network):
   if (dhcp == 1):
      interface = "auto " + eth + "\n\n"
   else: 
      interface = "auto " + eth + "\n"
      interface = interface + "iface " + eth + " inet static" + "\n"
      interface = interface + "address " + ip + "\n"
      interface = interface + "netmask 255.255.255.0\n"
      interface = interface + "broadcast " + broadcast + "\n"
      interface = interface + "network " + network + "\n"
   return(interface) 

def make_interfaces(interfaces, dhcps, ips, broadcasts, networks):

   etc_network_interfaces = """
auto lo 
iface lo inet loopback"""
   etc_network_interfaces = interfaces + "\n"

   idx = 0
   for eth in interfaces:
      etc_network_interfaces = etc_network_interfaces + make_interface(eth, dhcps[idx], ips[idx], broadcasts[idx], network[idx])
      idx = idx + 1

   etc_network_interfaces = etc_network_interfaces + "#post-up route add -net 192.168.176.0 netmask 255.255.255.0 gw 192.168.1.1\n"
   etc_network_interfaces = etc_network_interfaces + "post-up /home/ams/fireball_camera/iptables.sh\n" 

   return(etc_network_interfaces)


def get_rc_network():
   print ("YO")   



main()

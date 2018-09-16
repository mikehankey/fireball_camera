#!/usr/bin/python3
#this script sets up the cameras default params
# important backdoor URLS
# OSD - /videoosd.asp?
# Settings - /videolens.asp

import time
import requests
import sys
import os 
from amscommon import read_config
config = {}
if sys.argv[1] == 'ip':
   config['cam_ip'] = sys.argv[2]
   cam_num = sys.argv[3]
else:
   try:
      cam_num = sys.argv[1]
      config_file = "conf/config-" + cam_num + ".txt"
      config = read_config(config_file)
   except:
      config = read_config(config_file)

cam_ip = config['cam_ip']
print (config['cam_ip'])
config['cam_pwd'] = "xrp23q"

#config = read_config()

#try: 
#   cam_ip = sys.argv[1] 
#except: 
#   cam_ip = config['cam_ip']


#device_id = config['device_id']

print ("Setting up defaults for camera on IP address:", cam_ip)

print ("Set timezone and NTP server.")
url = "http://" + str(cam_ip) + "/cgi-bin/date_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&timezone=14&ntpHost=clock.isc.org"
print (url)
r = requests.get(url)
print (r.text)


print ("Set the OSD settings.")
url = "http://" + str(cam_ip) + "/cgi-bin/textoverlay_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&channel=0&Title=" + str("AMS") + "&DateValue=1&TimeValue=1&WeekValue=0&BitrateValue=0&Color=2&TitleValue=0"
print (url)
r = requests.get(url)
print (r.text)

url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=2000&paramchannel=0&paramcmd=2005&paramctrl=0&paramstep=0&paramreserved=0"
print (url)
for x in range(0,140):
    r = requests.get(url)
    print (r.text)


url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=2000&paramchannel=0&paramcmd=2006&paramctrl=0&paramstep=0&paramreserved=0"
print (url)
for x in range(0,134):
    r = requests.get(url)
    print (r.text)

#LSC CLOSE 
url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1048&paramctrl=0&paramstep=0&paramreserved=0"
print (url)
r = requests.get(url)
print (r.text)

#CTB COLOR 
url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1036&paramctrl=0&paramstep=0&paramreserved=0"
print (url)
r = requests.get(url)
print (r.text)

#WDR Closed
#url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1037&paramctrl=0&paramstep=0&paramreserved=0"
#print (url)
#r = requests.get(url)
#print (r.text)

#3D-DNR Normal
url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1049&paramctrl=3&paramstep=0&paramreserved=0"
print (url)
r = requests.get(url)
print (r.text)

url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1050&paramctrl=3&paramstep=0&paramreserved=0"
print (url)
r = requests.get(url)
print (r.text)

# IR CONTROL TO TIME UTC 5pm to 7am open it up
#url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1063&paramctrl=1&paramstep=0&paramreserved=0"
#print (url)
#r = requests.get(url)
#print (r.text)

#url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1081&paramctrl=1&paramstep=0&paramreserved=0"
#print (url)
#r = requests.get(url)
#print (r.text)



#url = "http://" + str(cam_ip) + "/webs/videoLensCfgEx?irtodayh=11&irtonighth=20"
#print (url)
#r = requests.get(url)
#print (r.text)

# default shutter speed of 50

r = requests.get("http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=50&paramstep=0&paramreserved=0&")

#os.system("./camera-settings.py " + str(cam_num) )
print ("Set the video encoding params.")
url = "http://" + str(cam_ip) + "/cgi-bin/videocoding_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&channel=0&EncType1=H.264&Resolution1=1920*1080&BitflowType1=VBR&KeyInterval1=5&Bitrate1=2048&FrameRate1=25&Profile1=High Profile&PicLevel1=1"

#time.sleep(45)
print (url)
r = requests.get(url)
print (r.text)

url = "http://" + str(cam_ip) + "/cgi-bin/videocoding_cgi?action=set&user=admin&pwd="+ config['cam_pwd'] +"&channel=0&EncType2=H.264&Resolution2=640*480&KeyInterval2=25&FrameRate2=25&BitflowType2=VBR&NormalBitrate2=1024&PicLevel2=1&Profile2=Main Profile&quality2=1&ratectrl2=1"
print (url)
r = requests.get(url)
print (r.text)


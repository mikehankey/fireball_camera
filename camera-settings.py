#!/usr/bin/python3

import sys
import time
from collections import defaultdict
from amscommon import read_config, read_sun
import os
import requests
from urllib.request import urlretrieve

def custom_settings (mode, config):
   file = open("/home/pi/fireball_camera/cam_calib/"+mode, "r")
   for line in file:
      line = line.strip('\n')
      c = line.index('=')
      config[line[0:c]] = line[c+1:]
   return(config)

def fix_ir(config ):
   print ("Fixing IR settings.")
   cam_ip = config['cam_ip']

   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1063&paramctrl=0&paramstep=0&paramreserved=0"
   r = requests.get(url)
   #print (r.text)

   time.sleep(1)
   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1047&paramctrl=0&paramstep=0&paramreserved=0"
   r = requests.get(url)
   #print (r.text)


   # open or close
   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1081&paramctrl=1&paramstep=0&paramreserved=0"
   r = requests.get(url)
   #print (r.text)

   #ir direction
   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1067&paramctrl=1&paramstep=0&paramreserved=0"
   r = requests.get(url)
   #print (r.text)

   time.sleep(1)
   # high low ICR
   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1066&paramctrl=0&paramstep=0&paramreserved=0"
   r = requests.get(url)
   #print (r.text)

def set_setting(config, setting, value):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=set&user=admin&pwd=" + config['cam_pwd'] + "&action=get&channel=0&" + setting + "=" + str(value)
   r = requests.get(url)
   return(r.text)

def get_settings(config):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=get&user=admin&pwd=" + config['cam_pwd'] + "&action=get&channel=0"
   print (url)
   settings = defaultdict()
   r = requests.get(url)
   resp = r.text
   for line in resp.splitlines():
      (set, val) = line.split("=")
      settings[set] = val
   return(settings)

def set_special(config, field, value):
   url = "http://" + str(config['cam_ip']) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=" + str(field) + "&paramctrl=" + str(value) + "&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

def WDR(config, on):
   #WDR ON/OFF 
   url = "http://" + str(config['cam_ip']) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1037&paramctrl=" + str(on) + "&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

def nighttime_settings( config):
   print ("Nighttime settings...")
   WDR(config, 0)
   time.sleep(1)
   fix_ir(config)
   ### BLC 
   set_special(config, "1017", "30")
   #set_setting(config, "Brightness", config['Brightness'])
   #set_setting(config, "Contrast", config['Contrast'])
   set_setting(config, "Gamma", config['Gamma'])
   set_setting(config, "InfraredLamp", "low")
   set_setting(config, "TRCutLevel", "low")
   file = open("/home/pi/fireball_camera/status" + cam_num + ".txt", "w")
   file.write("dark")
   file.close()

def daytime_settings(config):
   ### 
   WDR(config, 1)
   time.sleep(2)
   WDR(config, 0)
   time.sleep(2)
   WDR(config, 1)
   time.sleep(2)
   ### IR mode
   #set_special(config, "1064", "2")
   ### BLC 
   set_special(config, "1017", "30")

   set_setting(config, "Brightness", config['Brightness'])
   set_setting(config, "Gamma", config['Gamma'])
   set_setting(config, "Contrast", config['Contrast'])
   #set_setting(config, "InfraredLamp", "low")
   #set_setting(config, "TRCutLevel", "low")
   file = open("/home/pi/fireball_camera/status" + cam_num + ".txt", "w")
   file.write("day")
   file.close()



config_file = ""

try:
   cam_num = sys.argv[1]
   config_file = "conf/config-" + cam_num + ".txt"
   config = read_config(config_file)
except:
   config = read_config(config_file)
   cam_num = ""

print (config['cam_ip'])
fp = open("/home/pi/fireball_camera/calnow"+str(cam_num), "w")

#config = read_config()

settings = get_settings(config)

try:
   file = open("/home/pi/fireball_camera/status" + cam_num + ".txt", "r")
   cam_status = file.read()
   print ("CAM STATUS: ", cam_status)
except:
   print ("no cam status file exits.")
   cam_status = ""

#print (settings)

min_daytime_brightness = 100
max_nighttime_brightness = 120

sun = read_sun()

print (sun['status'])

if sun['status'] == 'day' or sun['status'] == 'dusk' or sun['status'] == 'dawn':
   config = custom_settings("Day", config)
   if cam_status != sun['status']:
      print ("Daytime settings are not set but it is daytime!", cam_status, sun['status'])
      #os.system("python /home/pi/fireball_camera/cam/auto_set_parameters.py")
      daytime_settings(config)
   else:
      print ("Daytime Brightness of " + settings['Brightness'] + " is fine.")
else:
   config = custom_settings("Night", config)
   if cam_status != sun['status']:
      print ("Nighttime settings are not set but it is nighttime!", cam_status, sun['status'])
      nighttime_settings(config)

os.system("./auto-brightness.py " + cam_num)
time.sleep(7)
os.system("rm /home/pi/fireball_camera/calnow"+str(cam_num))

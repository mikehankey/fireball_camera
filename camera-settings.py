#!/usr/bin/python3

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


def set_setting(config, setting, value):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=set&user=admin&pwd=" + config['cam_pwd'] + "&action=get&channel=0&" + setting + "=" + str(value)
   r = requests.get(url)
   return(r.text)

def get_settings(config):
   url = "http://" + str(config['cam_ip']) + "/cgi-bin/videoparameter_cgi?action=get&user=admin&pwd=" + config['cam_pwd'] + "&action=get&channel=0"
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
   fp = open("/home/pi/fireball_camera/calnow", "w")
   WDR(config, 0)
   ### BLC 
   set_special(config, "1017", "150")
   set_setting(config, "Brightness", config['Brightness'])
   set_setting(config, "Contrast", config['Contrast'])
   set_setting(config, "Gamma", config['Gamma'])
   set_setting(config, "InfraredLamp", "low")
   set_setting(config, "TRCutLevel", "low")
   time.sleep(5)
   os.system("rm /home/pi/fireball_camera/calnow")

def daytime_settings(config):
   fp = open("/home/pi/fireball_camera/calnow", "w")
   ### 
   WDR(config, 1)
   ### IR mode
   set_special(config, "1064", "2")
   ### BLC 
   set_special(config, "1017", "75")

   set_setting(config, "Brightness", config['Brightness'])
   set_setting(config, "Gamma", config['Gamma'])
   set_setting(config, "Contrast", config['Contrast'])
   set_setting(config, "InfraredLamp", "low")
   set_setting(config, "TRCutLevel", "low")
   os.system("rm /home/pi/fireball_camera/calnow")
   time.sleep(5)

config = read_config()

settings = get_settings(config)

sun = read_sun()
print (sun['status'])
if sun['status'] == 'day' or sun['status'] == 'dusk' or sun['status'] == 'dawn':
   config = custom_settings("Day", config)
   if settings['Brightness'] != config['Brightness']:
      daytime_settings(config)
else:
   config = custom_settings("Night", config)
   if settings['Brightness'] != config['Brightness']:
      nighttime_settings(config)

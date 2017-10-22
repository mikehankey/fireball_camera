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

def fix_ir(config ):
   # IR CONTROL TO TIME UTC 5pm to 7am open it up
   cam_ip = config['cam_ip']

   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1063&paramctrl=0&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1047&paramctrl=0&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

   # open or close
   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1066&paramctrl=2&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1081&paramctrl=1&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

   url = "http://" + str(cam_ip) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1067&paramctrl=0&paramstep=0&paramreserved=0"
   print (url)
   r = requests.get(url)
   print (r.text)

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
   fp = open("/home/pi/fireball_camera/calnow", "w")
   print ("Nighttime settings...")
   WDR(config, 0)
   time.sleep(2)
   ### BLC 
   set_special(config, "1017", "30")
   set_setting(config, "Brightness", config['Brightness'])
   set_setting(config, "Contrast", config['Contrast'])
   set_setting(config, "Gamma", config['Gamma'])
   set_setting(config, "InfraredLamp", "low")
   set_setting(config, "TRCutLevel", "low")
   time.sleep(15)
   os.system("rm /home/pi/fireball_camera/calnow")

def daytime_settings(config):
   fp = open("/home/pi/fireball_camera/calnow", "w")
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
   set_setting(config, "InfraredLamp", "low")
   set_setting(config, "TRCutLevel", "low")
   os.system("rm /home/pi/fireball_camera/calnow")
   time.sleep(5)

config = read_config()

settings = get_settings(config)

print (settings)

min_daytime_brightness = 100
max_nighttime_brightness = 60


sun = read_sun()
fix_ir(config)

print (sun['status'])
if sun['status'] == 'day' or sun['status'] == 'dusk' or sun['status'] == 'dawn':
   config = custom_settings("Day", config)
   if int(settings['Brightness']) < min_daytime_brightness:
      os.system("python /home/pi/fireball_camera/cam/auto_set_parameters.py")
      daytime_settings(config)
else:
   config = custom_settings("Night", config)
   if int(settings['Brightness']) > max_nighttime_brightness:
      nighttime_settings(config)
      os.system("python /home/pi/fireball_camera/cam/auto_set_parameters.py")

os.system("./auto-brightness.py")

#!/usr/bin/python3 
import ephem
import time
import sys
import os

# Add ../ for amscommon
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amscommon import read_config, write_config

# Add ../pw for crypt
sys.path.insert(1, os.path.join(sys.path[0], '../pwd'))
from crypt import Crypt

config = read_config() 

def deg_to_dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]
 
 
config = read_config()

print(config);


obs = ephem.Observer()
obs.pressure = 0
obs.horizon = '-0:34'
#print (deg_to_dms(float(config['device_lat'])))
#print (deg_to_dms(float(config['device_lng'])))
obs.lat = config['device_lat']
obs.lon = config['device_lng']
cur_date = time.strftime("%Y/%m/%d %H:%M") 
print ("CUR DATE: ", cur_date)
obs.date = cur_date

sun = ephem.Sun()
sun.compute(obs)

#print (obs.lat, obs.lon, obs.date)

(sun_alt, x,y) = str(sun.alt).split(":")
print ("Sun Alt: %s" % (sun_alt))

saz = str(sun.az)
(sun_az, x,y) = saz.split(":")
print ("SUN AZ IS : %s" % sun_az)
print ("CAM FOV IS : %s to %s " % (config['az_left'], config['az_right']))

if (int(sun_az) >= config['az_left'] and int(sun_az) <= config['az_right']):
   print ("Uh Oh... Sun is in the cam's field of view.")
   fov=1
else:
   print ("Sun is not in the cam's field of view")
   fov=0

#print (obs.previous_rising(ephem.Sun()))
#print (obs.next_setting(ephem.Sun()))
if int(sun_alt) < -3:
   dark = 1
else:
   dark = 0

if int(sun_alt) < -3:
   status = "dark";
if int(sun_alt) > -3 and int(sun_alt) < 5:
      if int(sun_az) > 0 and int(sun_az) < 180:
         status = "dawn"
      else:
         status = "dusk"
if int(sun_alt) >= 5:
   status = "day"


sun_file = open("/home/pi/fireball_camera/sun.txt", "w")
sun_info = "az=" + str(sun_az) + "\n"
sun_info = sun_info + "el=" + str(sun_alt) + "\n"
sun_info = sun_info + "fov=" + str(fov) + "\n"
sun_info = sun_info + "dark=" + str(dark) + "\n"
sun_info = sun_info + "status=" + str(status) + "\n"
sun_file.write(sun_info)



#!/usr/bin/python3 
import ephem
import time
import sys
import os
import json

# Add ../ for amscommon
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../config')))
from config_func import read_config_raw 
 

# Convert deg to dms  
def deg_to_dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]
 

# Get Sun Info From Device Position
def get_sun_info() : 

    config = read_config_raw()

    obs = ephem.Observer()
    obs.pressure = 0
    obs.horizon = '-0:34'
    obs.lat = config['device_lat']
    obs.lon = config['device_lng']
    cur_date = time.strftime("%Y/%m/%d %H:%M") # Get Current Date 
    obs.date = cur_date

    sun = ephem.Sun()
    sun.compute(obs)

    (sun_alt, x,y) = str(sun.alt).split(":")
    
    #Sun Altitude
    #print ("Sun Alt: %s" % (sun_alt))

    saz = str(sun.az)
    (sun_az, x,y) = saz.split(":")
    
    #print ("SUN AZ IS : %s" % sun_az)
    #print ("CAM FOV IS : %s to %s " % (config['az_left'], config['az_right']))

    if (int(sun_az) >= config['az_left'] and int(sun_az) <= config['az_right']):
        #print ("Uh Oh... Sun is in the cam's field of view.")
        fov=1
    else:
        #print ("Sun is not in the cam's field of view")
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

    # UPDATE sun.txt
    sun_file = open("/home/pi/fireball_camera/sun.txt", "w")
    sun_file.write("az=" + str(sun_az) + "\n"  + "el=" + str(sun_alt) + "\n" + "fov=" + str(fov) + "\n"  + "dark=" + str(dark) + "\n" + "status=" + str(status) + "\n")
    sun_file.close()
    
    # RETURN ARRAY OF DATA
    return json.dumps({'az':sun_az,'el':sun_alt,'fov':fov,'dark':dark,'status':status} , ensure_ascii=False, encoding="utf-8") 

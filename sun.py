import ephem
import time

def deg_to_dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
      #print key, value

    config['az_left'] = int(config['cam_heading']) - (int(config['cam_fov_x'])/2)
    config['az_right'] = int(config['cam_heading']) + (int(config['cam_fov_x'])/2)
    if (config['az_right'] > 360):
       config['az_right'] = config['az_right'] - 360
    if (config['az_left'] > 360):
       config['az_left'] = config['az_left'] - 360
    if (config['az_left'] < 0):
       config['az_left'] = config['az_left'] + 360
    config['el_bottom'] = int(config['cam_alt']) - (int(config['cam_fov_y'])/2)
    config['el_top'] = int(config['cam_alt']) + (int(config['cam_fov_y'])/2)
    return(config)


config = read_config()


obs = ephem.Observer()
obs.pressure = 0
obs.horizon = '-0:34'
#print (deg_to_dms(float(config['cam_lat'])))
#print (deg_to_dms(float(config['cam_lon'])))
obs.lat = config['cam_lat']
obs.lon = config['cam_lon']
cur_date = time.strftime("%Y/%m/%d %H:%M") 
obs.date = cur_date

sun = ephem.Sun()
sun.compute(obs)

#print (obs.lat, obs.lon, obs.date)
print ("Sun Alt: %s, Sun AZ: %s" % (sun.alt, sun.az))

saz = str(sun.az)
(sun_az, x,y) = saz.split(":")
print ("SUN AZ IS : %s" % sun_az)
print ("CAM FOV IS : %s to %s " % (config['az_left'], config['az_right']))

if (int(sun_az) >= config['az_left'] and int(sun_az) <= config['az_right']):
   print ("Uh Oh... Sun is in the cam's field of view.")
else:
   print ("Sun is not in the cam's field of view")

#print (obs.previous_rising(ephem.Sun()))
#print (obs.next_setting(ephem.Sun()))



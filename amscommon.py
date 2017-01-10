def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
    config['hd'] = 0
    file.close()
    return(config)

def write_config(config):
    if len(config) < 3:
       print ("Error not enough config vars passed.")
       exit()
    file = open("config.txt", "w")
    for key in config:
      line = key + "=" + config[key] + "\n"
      file.write(line)
    file.close()
    print ("Config written.")

def read_sun():
    sun_info = {}
    file = open("sun.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      sun_info[data[0]] = data[1]
    return(sun_info)

def put_device_info(conf):
   import requests
   import mimetypes
   import sys
   import netifaces 

   # PUT DEVICE INFO
   #api_key = "QwCsPJKr87y15Sy"
   #api_key = "7oZl2o7erVCq7gZ"
   #device_id  = 1
   url = "http://www.amsmeteors.org/members/api/cam_api/put_device_info"

   try:
      eth0_ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
   except:
      eth0_ip = "0.0.0.0"
   try:
      wlan0_ip= netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
   except:
      wlan0_ip = "0.0.0.0"


   # The Data to send with the file
   _data= {
      # required
      'api_key': conf['api_key'],
      'device_id': conf['device_id'],

      # optional
      # USER CAN'T CHANGE
      # MISSING
      'wlan_ip': wlan0_ip,
      'lan_ip': eth0_ip,
      'cam_ip': conf['cam_ip'],
      'heading': conf['heading'],
      'elv_angle': conf['elv_angle'],
      'pixel_scale': conf['pixel_scale'],

      # chip geoloc
   }

   _data['device_lat'] = conf['device_lat']
   _data['device_lon'] = conf['device_lon']
   _data['device_elv'] = conf['device_elv']

   fov = open('/home/pi/fireball_camera/fov.txt', 'r').read().replace('\n', '|')
   _data['fov'] = fov 

   _data['format'] = 'json'
   #print(fov)
   #print(_data)

   #session = requests.Session()
   #del session.headers['User-Agent']
   #del session.headers['Accept-Encoding']

   print (url)
   print (_data)
  
   r = requests.post(url, data=_data) 
   print (r.text)
   

   #with requests.Session() as session:
   #   response = session.post(url, data= _data)
   #print (response)
   #response.raw.close()

def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
    return(config)


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

   # PUT DEVICE INFO
   #api_key = "QwCsPJKr87y15Sy"
   api_key = "7oZl2o7erVCq7gZ"
   device_id  = 1
   url = "http://dev.amsmeteors.vm/members/api/cam_api/put_device_info"

   # The Data to send with the file
   _data= {
      # required
      'api_key': conf['api_key'],
      'device_id': conf['device_id'],

      # optional
      # USER CAN'T CHANGE
      # MISSING
      'wlan_ip': conf['wlan_ip'],
      'lan_ip': conf['lan_ip'],
      'cam_ip': conf['cam_ip'],
      'fov': conf['fov'],
      'heading': conf['heading'],
      'elv_angle': conf['elv_angle'],
      'pixel_scale': conf['pixel_scale'],

      # chip geoloc
   }

   try: 
      _data.append({'device_lat': conf['device_lat']})
   except:
      print ("skipping field.")
   try: 
      _data.append({'device_lon': conf['device_lon']})
   except:
      print ("skipping field.")
   try: 
      _data.append({'device_elv': conf['device_elv']})
   except:
      print ("skipping field")
   try:
      _data.append({'format': 'json'})
   except:
      print ("skipping field")

   session = requests.Session()
   del session.headers['User-Agent']
   del session.headers['Accept-Encoding']

   with requests.Session() as session:
      response = session.post(url, data= _data)

   print (response.text)
   response.raw.close()

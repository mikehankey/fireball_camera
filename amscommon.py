# Add ../pw for crypt
import sys
import os
import settings
 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './pwd')))
from crypt import Crypt
  
def caldate(caldate):
   y = caldate[0:4]
   m = caldate[4:6]
   d = caldate[6:8]
   h = caldate[8:10]
   mm = caldate[10:12]
   s = caldate[12:14]
   caldate = y + "-" + m + "-" + d + " " + h + ":" + mm + ":" + s 
   return(caldate)

def read_config(config_file = ""):
    print ("Reading: ", config_file)
    config = {}
    if config_file == "":
       file = open("/home/pi/fireball_camera/config.txt", "r")
    else:
       file = open(config_file, "r")
    
    for line in file:
      line = line.strip('\n')
      
      #Find first index of =
      c = line.index('=')
      config[line[0:c]] = line[c+1:]
    try:  
       test = config['hd'] 
    except:
       config['hd'] = 0
    
    if 'cam_pwd' in config:
        try:
            #We decrypt the cam password if it is crypted
            c = Crypt() 
            config['cam_pwd']  = c.decrypt(config['cam_pwd'])
        except:
             config['cam_pwd'] = config['cam_pwd']
    else: 
       config['cam_pwd'] = 'xrp23q';
    
    file.close()
    return(config)

def write_config(config, config_file = ""):
    if len(config) < 3:
       print ("Error not enough config vars passed.")
       exit()
    if config_file == "":
       file = open("/home/pi/fireball_camera/config.txt", "w")
    else:
       file = open(config_file, "w")
    for key in config:
      if key == 'cam_pwd':
        try:
            #We ecrypt the cam password if it is not crypted
            c = Crypt() 
            temp = c.decrypt(config['cam_pwd'])
        except:
             config['cam_pwd']  = c.encrypt(config['cam_pwd'])
   

      if key != 'IP':
         if key == 'cam_ip' and config[key] == '192.168.1.88':
            print ("skip.");
         else:
            line = key + "=" + str(config[key]) + "\n"
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
   import settings

   # PUT DEVICE INFO
   #device_id  = 1
   url = settings.API_SERVER + "members/api/cam_api/put_device_info"

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

      # chip geoloc
   }

   _data['device_lat'] = conf['device_lat']
   _data['device_lon'] = conf['device_lng']
   _data['device_alt'] = conf['device_alt']
   try:
      _data['heading'] = conf['heading']
      _data['elv_angle'] = conf['elv_angle']
      _data['pixel_scale'] =  conf['pixel_scale']
   except:
      print ("Not calibrated yet.")
   try:
      fov = open('/home/pi/fireball_camera/fov.txt', 'r').read().replace('\n', '|')
      _data['fov'] = fov 
   except: 
      fov = ""

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
   #response = session.post(url, data= _data)
   #print (response)
   #response.raw.close()

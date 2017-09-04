import os
import sys
import json
import logging
import requests

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import settings

logging.basicConfig(filename='/home/pi/fireball_camera/log_files/app.log',format='%(asctime)s -- %(levelname)s: --  %(message)s', datefmt='%m/%d/%Y %H:%M:%S',level=logging.DEBUG)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../pwd')))
from crypt import Crypt


# Get Device Info from the API and return the new config file
def get_device_info_and_config():
    config = read_config_raw() 

    # Get Device Info and Update device_info.txt
    r = requests.get(settings.API_SERVER + 'members/api/cam_api/get_device_info?format=json&LAN_MAC=' + config['lan_mac'] + '&WLAN_MAC=' + config['wlan_mac'])
    fp = open("device_info.txt", "w+")  
    fp.write(r.text)
    fp.close() 
    data = json.loads(r.text)

    # If the cam has already been claimed, we will have a 'result'
    if 'result' in data:
 
        for key in data['result']:
    
            # Here type of key = dict
            for k in key.values():
    
                for kk in k[0]:
    
                    # WE DONT PUT THE INFO THAT ARE JUST STRING (like geoloc_src for instance)
                    if(isinstance(type(k[0][kk]), basestring)): 
                        add_to_config(kk,k[0][kk])
    
        update_API_with_config() 
        config = read_config_raw() 
        return json.dumps(config, ensure_ascii=False, encoding="utf-8")
    
    else:
        config = read_config_raw() 
        config['error_claimed'] = 'Cam not claimed'

        # We remove the eventual data that shouldn't be here anymore
        # since the camera isnot claimed
        remove_from_config(['user_id','api_key','first_name','last_name','email']) 
 
        return json.dumps(config, ensure_ascii=False, encoding="utf-8") 


# Read Config File (Read the API first to get the latest updates from the API)
def read_config():

    logging.debug('Reading Config.txt')
    config = {}
    
    try: 
        file = open("/home/pi/fireball_camera/config.txt", "r")
        
        for line in file:
          line = line.strip('\n')
          
          #Find first index of =
          if('=' in line):
              c = line.index('=')
              config[line[0:c]] = line[c+1:]
        
        config['hd'] = 0
        
        if 'cam_pwd' in config:
            
            try:
                #We decrypt the cam password if it is crypted
                c = Crypt() 
                config['cam_pwd']  = c.decrypt(config['cam_pwd'])
                logging.debug('cam_pwd successfully decrypted')
            except:
                config['error'] = "Impossible to decrypt the password - password must only contains characters and digits"
                logging.error('Impossible to decrypt ' +  str(config['cam_pwd']))
                logging.debug('Config (ERROR) ' + str(config))
                
        file.close()
        logging.debug('Result ' + str(config) )
        
        return(config)
    except:
        config['error'] = 'The config file cannot be read, please check your config.txt file';
        logging.error('Error in config.txt')
        logging.debug('Config (ERROR) ' + str(config))
    return config;

    

# Return the config as a JSON object
def get_config():
    config = read_config_raw();
    return json.dumps(config, ensure_ascii=False, encoding="utf-8")

# Read the config file and parse FOV & EL
# And returns array
def read_config_raw():
  
    config = read_config() 
    
    try:
        config['az_left']  = int(config['cam_heading']) - (int(config['cam_fov_x'])/2)
        config['az_right'] = int(config['cam_heading']) + (int(config['cam_fov_x'])/2)
        if (config['az_right'] > 360):
            config['az_right']  = config['az_right'] - 360
        if (config['az_left'] > 360):
            config['az_left']   = config['az_left'] - 360
        if (config['az_left'] < 0):
            config['az_left']   = config['az_left'] + 360
            config['el_bottom'] = int(config['cam_alt']) - (int(config['cam_fov_y'])/2)
            config['el_top']    = int(config['cam_alt']) + (int(config['cam_fov_y'])/2)
        config['calibration']   = '1' #Calibration Done  
        logging.debug('Calibration info computed from config.txt')
    except:
        config['az_left']   = 0
        config['az_right']  = 0
        config['calibration'] = '0' #Calibration TO BE DONE
        logging.warning('Calibration info missing in config.txt')
    return config;


# Remove a value from the config file 
# The function is used when the camera has been unclaimed from the API
def remove_from_config(param):
    
    config = read_config_raw(); 
    i=0

    while i < len(param):
      if(param[i] in config):
        del config[param[i]]
      i += 1  
 
    file = open("/home/pi/fireball_camera/config.txt", "w")
    for key in config:
        value = config[key]
            
        if(key=='cam_pwd'):
            c     = Crypt()
            value = c.encrypt(value)
            
        line = str(key) + "=" + str(value) + "\n"
        file.write(line) 
                   
    file.close()


# Add or Update a param in the config file
# WARNING THIS FUNCTION DOESNT UPDATE THE cam_pwd ON THE CAMERA SIDE 
def add_to_config(param,new_value):
    #Read Current Config
    
    if(param!='cam_pwd'):
    
        config = read_config_raw();
        
        logging.debug('Try to update the config file with ' +  str(param) + ' = ' + str(new_value))
        
        updated = 0;
        
        #Loop throught config
        for key in config:
            
            if(key == param):
                config[key] = new_value
                updated = 1;
        
        # In case the param doesnt exist yet in the config file
        if(updated==0):
            config[param] = new_value
            logging.debug('The parameter ' + str(param) + ' didnt exist in config.txt')
            
        # We rewrite the config file
        # WARNING: we need to recrypt cam_pwd here as read_config_raw decrypt it   
        
        file = open("/home/pi/fireball_camera/config.txt", "w")
        
        for key in config:
            value = config[key]
            
            if(key=='cam_pwd'):
                c     = Crypt()
                value = c.encrypt(value)

            if(key!='error'):    
                line = str(key) + "=" + str(value) + "\n"
                file.write(line) 
                   
        file.close()
        
    else:
        logging.error('We tried to update cam_pwd with add_to_config: IMPOSSIBLE')


# UpdaAPI with info from config file
def update_API_with_config():
   import requests
   import mimetypes
   import sys
   import netifaces 
   import settings

   conf = read_config()

   # PUT DEVICE INFO 
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
      # optional
      # USER CAN'T CHANGE
      # MISSING
      'wlan_ip' : wlan0_ip,
      'lan_ip'  : eth0_ip, 
    }

   if('cam_ip' in conf):
        _data['cam_ip'] = conf['cam_ip']

   if('device_id' in conf):
        _data['device_id'] = conf['device_id']

   if('api_key' in conf):
        _data['api_key'] = conf['api_key']     

   if('device_lat' in conf):
        _data['device_lat'] = conf['device_lat']

   if('device_lng' in conf):
        _data['device_lon'] = conf['device_lng']

   if('device_alt' in conf):
        _data['device_alt'] = conf['device_alt']

   if('heading' in conf and 'elv_angle' in conf and  'pixel_scale' in conf):
        _data['heading'] = conf['heading']
        _data['elv_angle'] = conf['elv_angle']
        _data['pixel_scale'] =  conf['pixel_scale']         
 
 
   if(os.path.isfile('/home/pi/fireball_camera/fov.txt')):
        fov = open('/home/pi/fireball_camera/fov.txt', 'r').read().replace('\n', '|')
        _data['fov'] = fov 
   else:
        open('/home/pi/fireball_camera/fov.txt', 'w+')  

   _data['format'] = 'json'
   
   r = requests.post(url, data=_data)  
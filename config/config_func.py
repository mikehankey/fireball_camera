import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../pwd')))
from crypt import Crypt

# Read Config File
def read_config():
    config = {}
    file = open("/home/pi/fireball_camera/config.txt", "r")
    
    for line in file:
      line = line.strip('\n')
      
      #Find first index of =
      c = line.index('=')
      config[line[0:c]] = line[c+1:]
    
    config['hd'] = 0
    
    if 'cam_pwd' in config:
        try:
            #We decrypt the cam password if it is crypted
            c = Crypt() 
            config['cam_pwd']  = c.decrypt(config['cam_pwd'])
        except:
             config['cam_pwd'] = config['cam_pwd']
    
    file.close()
    return(config)

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
    except:
        config['az_left']   = 0
        config['az_right']  = 0
        config['calibration'] = '0' #Calibration TO BE DONE
    return config;


# Add or Update a param in the config file
# WARNING THIS FUNCTION DOESNT UPDATE THE cam_pwd ON THE CAMERA SIDE 
def add_to_config(param,new_value):
    #Read Current Config
    config = read_config_raw();
    
    updated = 0;
    
    #Loop throught config
    for key in config:
        
        if(key == param):
            config[key] = new_value
            updated = 1;
    
    # In case the param doesnt exist yet in the config file
    if(updated==0):
        config[param] = new_value
        
    # We rewrite the config file
    # WARNING: we need to recrypt cam_pwd here as read_config_raw decrypt it   
    
    file = open("/home/pi/fireball_camera/config.txt", "w")
    
    for key in config:
        value = config[key]
        
        if(key=='cam_pwd'):
            c     = Crypt()
            value = c.encrypt(value)
        
        line = str(key) + "=" + str(value) + "\n"
        file.write(line) 
               
    file.close()
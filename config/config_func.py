import os
import sys
import json
import logging


logging.basicConfig(filename='/home/pi/fireball_camera/log_files/app.log',format='%(asctime)s -- %(levelname)s: --  %(message)s', datefmt='%m/%d/%Y %H:%M:%S',level=logging.DEBUG)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../pwd')))
from crypt import Crypt

# Read Config File
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
                
        file.close()
        logging.debug('Result ' + str(config) )
        
        return(config)
    except:
        config['error'] = 'The config file cannot be read, please check your config.txt file';
        logging.error('Error in config.txt')
        logging.debug( str(config))
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
            
            line = str(key) + "=" + str(value) + "\n"
            file.write(line) 
                   
        file.close()
        
    else:
            logging.error('We tried to update cam_pwd with add_to_config: IMPOSSIBLE')

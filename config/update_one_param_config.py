import os
import sys

from config_func import read_config_raw

sys.path.insert(1, os.path.join(sys.path[0], '../pwd'))
from crypt import Crypt

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
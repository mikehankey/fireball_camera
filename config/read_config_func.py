import os
import sys

# Add ../ for amscommon
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amscommon import read_config, write_config

# Read the config file and parse FOV & EL
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

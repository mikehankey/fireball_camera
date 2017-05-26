import json
import os
import sys

# Add ../ for amscommon
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amscommon import read_config, write_config

# Add ../pw for crypt
sys.path.insert(1, os.path.join(sys.path[0], '../pwd'))
from crypt import Crypt

config = read_config() 
 
try:
    config['az_left']  = int(config['cam_heading']) - (int(config['cam_fov_x'])/2)
    config['az_right'] = int(config['cam_heading']) + (int(config['cam_fov_x'])/2)
    if (config['az_right'] > 360):
        config['az_right'] = config['az_right'] - 360
    if (config['az_left'] > 360):
        config['az_left'] = config['az_left'] - 360
    if (config['az_left'] < 0):
        config['az_left'] = config['az_left'] + 360
        config['el_bottom'] = int(config['cam_alt']) - (int(config['cam_fov_y'])/2)
        config['el_top'] = int(config['cam_alt']) + (int(config['cam_fov_y'])/2)
    # Calibration Done    
    config['calibration'] = '1'
except:
    config['az_left'] = 0
    config['az_right'] = 0
    # Calibration TO BE DONE
    config['calibration'] = '0'

print json.dumps(config, ensure_ascii=False, encoding="utf-8")
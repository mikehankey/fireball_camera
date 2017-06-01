import json
import os
import sys
from cam_functions import set_parameters

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../file_management')))
from read_param_file import read_file

#Ex: 
#python ./cam/get_parameter_from_file.py Night

# Open Right File [Night or Day or Calibration]
log_file  = "/home/pi/fireball_camera/cam_calib/" + sys.argv[1]
 
# Parse Data
data = read_file(log_file,'JSON')

# Update Cam Config
set_parameters([data])

# Return Data
print(data)
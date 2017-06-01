#UPDATE a cam_calib file with a specific value and update the camera value for preview purpose
import sys
import os 
import json 
from cam_functions import update_parameters

sys.path.insert(1, os.path.join(sys.path[0], '../config'))
from config_func import read_config 

# Update (live) Camera config
 
#Ex: 
#python ./cam/set_parameters_to_file.py '{"Brightness": 29, "file":"Night"}' 
  
config = read_config()
possible_values = ['Brightness','Contrast','Gamma','Chroma','File'];

# Get Parameters passed in arg
if(len(sys.argv)!=0):

    new_values  = json.loads(sys.argv[1])  
    file = new_values['file']
    del new_values['file'] 

    update_parameters(file,new_values)
 
else:
    print 'No Parameters to Update (argv)'

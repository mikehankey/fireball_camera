import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sun')))
from get_info_func import get_sun_info 

from cam_functions import upload_parameter_file 

#1- Get Sun Info 
sun_info =  json.loads(get_sun_info())
 
#2- Depending on the darkness: load night or day
if(sun_info['dark']== 0 ):
    parameters_file = 'Day'
else:
    parameters_file = 'Night'
    
upload_parameter_file(parameters_file)
    
#3- Return the name of the file loaded in the cam 
print(parameters_file)
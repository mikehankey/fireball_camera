import os
import sys
import urllib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../config')))
from read_config_func import read_config_raw 
from update_one_param_config import add_to_config 
 
def upload_parameter_file(parameters_file_name):
    file = open("/home/pi/fireball_camera/cam_calib/"+parameters_file_name, "r")
    
    parameters = ''
    
    for line in file:
      line = line.strip('\n')
      
      #Find first index of =
      c = line.index('=')
      parameters += '&' + line[0:c] + '=' +  str(line[c+1:])
  
    file.close()
    
    # Get the cam_pwd
    config = read_config_raw()
    
    # Update the cam live parameters
    fname = 'http://'+config['cam_ip']+'/cgi-bin/videoparameter_cgi?action=set&channel=0&user=admin&pwd='+config['cam_pwd'] + parameters
    
    # Call to CGI
    urllib.urlopen(fname)
    
    # Update the config file with the name of the set of parameters loaded
    add_to_config('parameters',parameters_file_name);
     
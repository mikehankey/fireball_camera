import sys
import os
import urllib
import json
import fileinput
import re

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config   

# Update (live) Camera config
 
#Ex: 
#python ./cam/set_parameters_to_file.py '{"Brightness": 29, "file":"Night"}' 
  
config = read_config()
possible_values = ['Brightness','Contrast','Saturation','Chroma','File'];


# Get Parameters passed in arg
if(len(sys.argv)!=0):
 
    new_values  = json.loads(sys.argv[1])  
    parameters = ''
    
    for key in new_values:
        if key in possible_values and key != 'file':
            parameters += '&' + key + '=' +  str(new_values[key])
     
    if(parameters != ''):
        # Set the new Cam Video Parameters
        fname = 'http://'+config['cam_ip']+'/cgi-bin/videoparameter_cgi?action=set&channel=0&user=admin&pwd='+config['cam_pwd'] + parameters
        
        # Call to CGI
        a = urllib.urlopen(fname)
        
        # Update File passed in argument (Night or Calibration or Day)
        if 'file' in new_values:
            log_file  = "/home/pi/fireball_camera/cam_calib/" + new_values['file']
            
            for key in new_values: 
                if key != 'file':
                    v = str(key)
                    r = re.compile(r"("+v+")=(\d*)")
          
                    for line in fileinput.input([log_file], inplace=True):
                        # Search the current value for  new_values[key]
                        newV = new_values[key]
                        print r.sub(r"\1=%s"%newV,line.strip()) 
                 
        print a.getcode()
 
    else:
        print 'No Parameters to Update'

else:
    print 'No Parameters to Update (argv)'

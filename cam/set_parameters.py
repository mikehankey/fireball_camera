import sys
import os
import urllib
import json

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config   

#Ex: 
#python ./cam/set_parameters.py '{"Brightness": 29}' 

 
config = read_config()
   
possible_values = ['Brightness','Contrast','Saturation','Chroma'];
   
#ex: .../cgi-bin/videoparameter_cgi?action=set&channel=0&user=admin&pwd=admin&Brightness=20&Contrast=100&Chroma=200&Saturation=123
   
# Get Parameters passed in arg
if(len(sys.argv)!=1):

    new_values  = json.loads(sys.argv[1]) # Config info
    
    parameters = ''
    
    for key in new_values:
        if key in possible_values:
            parameters += '&' + key + '=' +  str(new_values[key])
        
    
    if(parameters != ''):
        # Set the new Cam Video Parameters
        fname = 'http://'+config['cam_ip']+'/cgi-bin/videoparameter_cgi?action=set&channel=0&user=admin&pwd='+config['cam_pwd'] + parameters
        
        # Call to CGI
        urllib.urlopen(fname)
    
        print 'Parameters Updated'
 
    else:
        print 'No Parameters to Update'

else:
    print 'No Parameters to Update'

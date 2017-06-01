import sys
import os
import urllib
import json

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config   

# Update (live) Camera config
def set_parameters(argv): 

    #Ex: 
    #python ./cam/set_parameters.py '{"Brightness": 29}' 
      
    config = read_config()
    possible_values = ['Brightness','Contrast','Gamma','Chroma'];
   
    # Get Parameters passed in arg
    if(len(argv)!=0):
     
        new_values  = json.loads(argv[0])  
        parameters = ''
        
        for key in new_values:
            if key in possible_values:
                parameters += '&' + key + '=' +  str(new_values[key])
         
        if(parameters != ''):
            # Set the new Cam Video Parameters
            fname = 'http://'+config['cam_ip']+'/cgi-bin/videoparameter_cgi?action=set&channel=0&user=admin&pwd='+config['cam_pwd'] + parameters
            
            # Call to CGI
            a = urllib.urlopen(fname)
        
            #print a.getcode()
     
        else:
            print 'No Parameters to Update'
    
    else:
        print 'No Parameters to Update (argv)'

# UPDATE CONFIG FILE 
# WITH INFO PASSED AS JSON 

import sys
import os
import urllib
import json
import copy
import pprint

from config_func import read_config_raw

sys.path.insert(1, os.path.join(sys.path[0], '../pwd'))
from crypt import Crypt
  
config  = json.loads(sys.argv[1]) # Config info
 
file = open("/home/pi/fireball_camera/config.txt", "w")

tmp_config = copy.copy(config)

for key in config:

    value = config[key]
 
    # We need to update the cam password 
    if key == 'new_cam_pwd':
        
        
        # It is the first time
        if 'cam_pwd' in config:
        
            
            #Update the Cam Password via the cgi
            fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=update&user=admin&pwd='+config['cam_pwd']+'&username=admin&password='+value
            #print fname
            
            # Remove the old cam_pwd so we dont have 2 in the config file
            del tmp_config['cam_pwd']
          
        # It is not the first time
        else:
            
            
            #Update the Cam Password via the cgi
            fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=update&user=admin&pwd=admin&username=admin&password='+value
            #print fname
         
        # Call to CGI
        urllib.urlopen(fname)
         
        # Encrypt the Cam Password to store it in the config file
        c     = Crypt()
        value = c.encrypt(value)
      
        # Write new pwd in config.txt
        line = "cam_pwd=" + str(value) + "\n"
        file.write(line)
        
        del tmp_config['new_cam_pwd']

 
for key in tmp_config:
    value = tmp_config[key]
    line = str(key) + "=" + str(value) + "\n"
    file.write(line)
        
file.close()

#Read again before sending  
configN = read_config_raw();
print json.dumps(configN, ensure_ascii=False, encoding="utf-8")
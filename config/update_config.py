import sys
import os
import urllib
import json
import copy
import pprint

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config, write_config
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
configNEW = read_config() 

if 'cam_pwd' in configNEW:
    #We decrypt the cam password
    c = Crypt() 
    configNEW['cam_pwd'] = c.decrypt(configNEW['cam_pwd'])

print json.dumps(configNEW, ensure_ascii=False, encoding="utf-8")
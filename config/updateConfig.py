import sys
import os
import urllib
import json

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config, write_config
sys.path.insert(1, os.path.join(sys.path[0], '../pwd'))
from crypt import Crypt

print sys.argv[1]
jsonObject  = json.loads(sys.argv[1]) # Config info
 
file = open("/home/pi/fireball_camera/config.txt", "w")
for key in jsonObject:
 
    value = jsonObject[key]
    
    if(key=='cam_pwd'):
        c = Crypt()
        value = c.encrypt(value)
    
    line = key + "=" + str(value) + "\n"
    file.write(line)
file.close()

print "Config file updated"
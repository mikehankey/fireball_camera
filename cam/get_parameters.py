import sys
import os
import urllib
import json

sys.path.insert(1, os.path.join(sys.path[0], '../config'))
from config_func import read_config   
 
config = read_config()
   
# Get Cam Video Parameters
fname = 'http://'+config['cam_ip']+'/cgi-bin/videoparameter_cgi?action=get&channel=0&user=admin&pwd='+config['cam_pwd']
  
file = urllib.urlopen(fname)
param = {}
for line in file:
      line = line.strip('\n')
      
      #Find first index of =
      #modify to allow encoded pwds with '='
      c = line.index('=')
      param[line[0:c]] = line[c+1:]
    
 
file.close()
print json.dumps(param, ensure_ascii=False)
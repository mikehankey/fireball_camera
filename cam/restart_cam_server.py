import os
import sys
import urllib

sys.path.insert(1, os.path.join(sys.path[0], '../config'))
from config_func import read_config 
 
config = read_config() 
fname = 'http://'+config['cam_ip']+'/cgi-bin/restart_cgi?user=admin&pwd='+config['cam_pwd']
            
# Call to CGI
urllib.urlopen(fname)
 
print("Restarting")
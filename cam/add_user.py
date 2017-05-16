import sys
import os
import urllib

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config   
 
config = read_config()

# This function is used on mkdevice to add a admin user with the name/pwd 
# = config['last_name'][0].lower() + config['last_name'].lower()
# for the camera

http://192.168.88.187/cgi‐bin/pwdgrp_cgi?action=add&user=admin&pwd=admin&username=hanghe1234&password=123456&level=2


// Get list of users
#fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=get&user=admin&pwd=12345'

// Update admin password
#fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=update&user=admin&pwd=admin&username=admin&password=admin'

f = urllib.urlopen(fname)
myfile = f.read()
print myfile
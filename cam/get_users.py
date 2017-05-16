import sys
import os
import urllib

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config   


config = read_config()

// Get list of users
fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=get&user=admin&pwd=12345'

// Update admin password
#fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=update&user=admin&pwd=admin&username=admin&password=admin'

f = urllib.urlopen(fname)
myfile = f.read()
print myfile
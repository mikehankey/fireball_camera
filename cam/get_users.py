import sys
import os
import urllib
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from amscommon import read_config  
import re


config = read_config()
fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=get&user=admin&pwd=12345'

#fname = 'http://'+config['cam_ip']+'/cgi-bin/pwdgrp_cgi?action=update&user=admin&pwd=admin&username=admin&password=12345'

f = urllib.urlopen(fname)
myfile = f.read()
print myfile
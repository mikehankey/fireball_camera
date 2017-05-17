import json
import os
import sys

# Add ../ for amscommon
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from amscommon import read_config, write_config

# Add ../pw for crypt
sys.path.insert(1, os.path.join(sys.path[0], '../pwd'))
from crypt import Crypt

config = read_config()

print config

if 'cam_pwd' in config:
    #We decrypt the cam password
    c     = Crypt() 
    print "IN READ CONFIG2"
    print config['cam_pwd']
    config['cam_pwd'] = c.decrypt(config['cam_pwd'])

print json.dumps(config, ensure_ascii=False, encoding="utf-8")
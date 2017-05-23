import json
import os
import sys

# Add ../ for amscommon
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amscommon import read_config, write_config

# Add ../pw for crypt
sys.path.insert(1, os.path.join(sys.path[0], '../pwd'))
from crypt import Crypt

config = read_config() 
 
print json.dumps(config, ensure_ascii=False, encoding="utf-8")
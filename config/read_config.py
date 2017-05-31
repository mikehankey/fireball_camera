import json 

# Add ../ for amscommon
from read_config_func import read_config_raw
  
config = read_config_raw();
print json.dumps(config, ensure_ascii=False, encoding="utf-8")
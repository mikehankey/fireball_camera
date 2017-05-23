import json
import os
import sys
from set_parameters import set_parameters

#Ex: 
#python ./cam/get_parameter_from_file.py Night

# Open Right File [Night or Day or Calibration]
log_file  = "/home/pi/fireball_camera/cam_calib/" + sys.argv[1]
 
# Parse Data
data = {}
file = open(log_file, "r")
 
for line in file:
  line = line.strip('\n')
   
  #Find first index of =
  c = line.index('=')
  data[line[0:c]] = line[c+1:]

file.close()

# Update Cam Config
set_parameters([json.dumps(data, ensure_ascii=False, encoding="utf-8")])

# Return Data
print (json.dumps(data, ensure_ascii=False, encoding="utf-8"))

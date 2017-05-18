import json
import os
import sys
 
log_file  = "/home/pi/fireball_camera/log_files/" + sys.argv[1]
config = {}

new_entries  = json.loads(sys.argv[2]) # New Log Entries to add

if os.path.exists(log_file):
    file = file(log_file, "a") 
    
    for key in new_entries:
        line = key + "=" + str(new_entries[key]) + "\n"
        file.write(line)

    file.close()    
    
    
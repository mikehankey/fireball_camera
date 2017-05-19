import json
import os
import sys

#python write_log.py test1 '{"Log":"2018-25-00 00:00:00$18$25$25"}'
 
log_file  = "/home/pi/fireball_camera/log_files/" + sys.argv[1]
config = {}

new_entries  = json.loads(sys.argv[2]) # New Log Entries to add

if os.path.exists(log_file):

    with open(log_file, 'r') as original: data = original.read()
    with open(log_file, 'w') as modified: 

        for key in new_entries:
            line = key + "=" + str(new_entries[key]) + "\n"
            modified.write(line)

        modified.write(data)
        modified.close()  
        
        print "log updated" 
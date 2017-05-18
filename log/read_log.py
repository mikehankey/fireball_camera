import sys
import json
import os

log_file  = "/home/pi/fireball_camera/log_files/" + sys.argv[1]
config = {}

if os.path.exists(log_file):
    file = file(log_file, "r+")
else:
    file = file(log_file, "w+")

for line in file:
    line = line.strip('\n')
    index1 = line.index('=')
    data   = line[index1+1:].rsplit("$")
    res = {}
    text = ['Outside Temperature','Inside Temperature','Inside Humidity']
    c = 0
    for i in data:
        res[text[c]] = i
        c+=1
    config[line[0:index1]] = res
    
file.close()
print json.dumps(config, ensure_ascii=False, encoding="utf-8")
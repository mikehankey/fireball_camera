import sys
import json
import os

log_file  = "/home/pi/fireball_camera/log_files/" + sys.argv[1]
res = {}

if os.path.exists(log_file):
    file = file(log_file, "r+")
else:
    file = file(log_file, "w+")

line_n = 0
for line in file:
    line   = line.strip('\n')
    index1 = line.index('=')
    data   = line[index1+1:].rsplit("$")
    tmp_res = {}
    text = ['Time','Outside Temperature','Inside Temperature','Inside Humidity']
    c = 0
    for i in data:
        tmp_res[text[c]] = i
        c+=1
    #print tmp_res   
    res[str(line_n)] = tmp_res
    line_n += 1 
  
    
file.close()
print json.dumps(res, ensure_ascii=False, encoding="utf-8")
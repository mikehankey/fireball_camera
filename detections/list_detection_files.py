# RETURN ALL FILES FROM A FOLDER
# as a JSON Object

import glob
import os
import json
import re
import sys
from os import listdir
from os.path import isfile, join
 
def read_file(file_path):
    config = ''
    file = open(file_path, "r")
    for line in file:
        config = config + line
    file.close()
    return(config)


#List detections with pagination
#sys.argv[1] = path to detection folder
#sys.argv[2] = page to display
#sys.argv[3] = max detections per page
data = {"detection":[]}
c = 0

cur_page                = int(sys.argv[2])
max_detections_per_page = int(sys.argv[3])
 
#Get whole list of files
whole_list = glob.glob(sys.argv[1]+'*.avi')
data["total_detection"] = len(whole_list)
data["cur_page"]        = cur_page
data["total_page"]      = int(data["total_detection"])/max_detections_per_page 
data["max_per_page"]    = max_detections_per_page

for X in range((cur_page-1)*max_detections_per_page, cur_page*max_detections_per_page+max_detections_per_page):

    if(X<int(data["total_detection"])):

        filename = os.path.basename(whole_list[X])
        d = {}
        d['name'] = os.path.splitext(filename)[0]
          
        m = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', d['name'])
        
        if m:
             d['date'] =  m.group(1)+'-'+m.group(2)+'-'+m.group(3)+' '+m.group(4)+':'+m.group(5)+':'+m.group(6)
        
        d['video']   = d['name'] + ".avi"
        d['objects'] = d['name'] + "-objects.jpg"
        d['preview'] = d['name'] + ".jpg"
        
        #Try with -summary.txt
        sum_file  = sys.argv[1]+d['name'] + "-summary.txt" 
        if(os.path.isfile(sum_file)):
            d['summary']    = d['name'] + "-summary.txt"
            d['summaryTxt'] = read_file(sum_file)
        
        #Try with .txt only
        sum2_file  = sys.argv[1]+d['name'] + ".txt"
        if(os.path.isfile(sum2_file)):
            d['detail']    = d['name'] + ".txt"
            d['detailTxt'] = read_file(sum2_file)
        
        data["detection"].append({'detect': d})

print json.dumps(data)
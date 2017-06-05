# DELETE DETECTIONS FILES
# with the following extensions: ".jpg","-objects.jpg","-summary.txt",".avi",".txt"

import glob
import os 
import sys
from os.path import isfile
import os.path
import re
 
extensions  = [".jpg","-objects.jpg","-summary.txt",".avi",".txt"]
toReturn    = ''

#If we pass the ev as the 2nd arguments
if len(sys.argv) > 2:
    #Only the selects events
    events      = sys.argv[2].split(",")

    for event in events: 
        for ext in extensions: 
            f = sys.argv[1] + event + ext
            if os.path.isfile(f):
                os.remove(f)
                if ext in ['.txt']:
                    m = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', event)
                    if m:
                        event =  m.group(1)+'-'+m.group(2)+'-'+m.group(3)+' '+m.group(4)+':'+m.group(5)+':'+m.group(6)
                
                    toReturn = toReturn + '$' + event

else:
    #All the events
    events = glob.glob(sys.argv[1]+'*') 
    for f in events: 
        if os.path.isfile(f):
            filename, file_extension = os.path.splitext(f)
            os.remove(f)
            if file_extension in ['.txt']:
                        m = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', f)
                        if m:
                            f =  m.group(1)+'-'+m.group(2)+'-'+m.group(3)+' '+m.group(4)+':'+m.group(5)+':'+m.group(6)
                    
                        toReturn = toReturn + '$' + f
 
 
print toReturn
#Read a parameter file 
#ex:
#Brightness=128
#Contrast=128
#...

import json

# url_format=1 returns '&[KEY]=[VAL]'
# url_format=0 return JSON Object
def read_file(file, _format):
    if(_format=='JSON'):
        data = {}
    else:
        data = ""  
        
    file = open(file, "r")
     
    for line in file:
      line = line.strip('\n')
       
      #Find first index of =
      c = line.index('=')
      
      if(_format=='JSON'):
          data[line[0:c]] = line[c+1:]
      else:
          data += '&' + line[0:c] + '=' +  str(line[c+1:])
    
    file.close()
    
    if(_format=='JSON'):
        return json.dumps(data, ensure_ascii=False)    
    else:
        return data
        
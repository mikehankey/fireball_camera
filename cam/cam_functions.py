import os
import sys
import urllib
import json
import fileinput
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../config')))
from config_func import read_config_raw, add_to_config  

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../file_management')))
from read_param_file import read_file
 
# Update (live) Camera config
# FROM A JSON Object passed in agrv
def set_parameters(_file,argv): 

    #Ex: 
    #python ./cam/set_parameters.py '{"Brightness": 29}' 
      
    config = read_config_raw()
    possible_values = ['Brightness','Contrast','Gamma','Chroma'];

    # Get Parameters passed in arg
    if(len(argv)!=0):
     
        new_values = json.loads(argv[0])
 
        parameters = ''
        
        for key in new_values:
            if key in possible_values:
                parameters += '&' + key + '=' +  str(new_values[key])
         
        if(parameters != ''):
             # Get Specific Parameters
             parameters = update_specific_param(parameters,_file)

             # Update Cam Parameters
             update_cam(parameters)
       
        else:
            print 'No Parameters to Update'
    
    else:
        print 'No Parameters to Update (argv)'
        
         
#Set special parameters to cam
def set_special(config, field, value):
    fname = "http://" + str(config['cam_ip']) + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=" + str(field) + "&paramctrl=" + str(value) + "&paramstep=0&paramreserved=0"
    # Call to CGI
    urllib.urlopen(fname) 

 
# Update Camera parameters
# With parameters passed as URL string (&[key]=[val]&...)
def update_cam(parameters):
    # Get the cam_pwd
    config = read_config_raw()
    
    # Update the cam live parameters
    fname = 'http://'+config['cam_ip']+'/cgi-bin/videoparameter_cgi?action=set&channel=0&user=admin&pwd='+config['cam_pwd'] + parameters
  
    # Call to CGI
    urllib.urlopen(fname)
 
 

# Update specific parameters depending on the param file select (Night/Day/Calibration)
def update_specific_param(parameters,parameters_file_name):
    
    # Get the cam_pwd & ip
    config = read_config_raw()

    #Add Specific parameters for calib/day/night
    if(parameters_file_name=='Night'):
        
        #Add to parameters string
        parameters+= "&InfraredLamp=high"
        parameters+= "&TRCutLevel=high"

        ### BLC 
        #set_special(config, "1017", "75")
        ## WR - ON
        set_special(config, "1037", "0") 

    elif(parameters_file_name=='Day'): 

        ### BLC 
        #set_special(config, "1017", "150")
        ## WR - OFF
        set_special(config, "1037", "1")

        #Add to parameters string
        parameters+= "&InfraredLamp=low"
        parameters+= "&TRCutLevel=low"
 
    return parameters    


# Update live camera parameters with parameters contained 
# in the file passed "parameters_file_name"
# ex: upload_parameter_file('Night')
def upload_parameter_file(parameters_file_name):
 
    file =  "/home/pi/fireball_camera/cam_calib/"+parameters_file_name;
    
    # Parse Data (URL Format)
    parameters = read_file(file,"URL") 

   
    # Get Specific Parameters
    parameters = update_specific_param(parameters,parameters_file_name)

    # Update Cam Parameters
    update_cam(parameters)

    # Update the config file with the name of the set of parameters loaded
    add_to_config('parameters',parameters_file_name)
 

# Update Parameter File 
# and the camera live setting at the same time (used form preview)
def update_parameters(_file,new_values):
    possible_values = ['Brightness','Contrast','Gamma','Chroma','File'] 
    parameters = ''

    # Build the parameters URL string
    for key in new_values:
        if key in possible_values and key != 'file' and key != 'File':
            parameters += '&' + key + '=' +  str(new_values[key])
     
    if(parameters != ''):
 
         # Get Specific Parameters
        parameters = update_specific_param(parameters,_file)

         # Update Cam Parameters
        update_cam(parameters)
        
        # Replace only the new values passed in the calib file
        log_file  = "/home/pi/fireball_camera/cam_calib/" + _file
            
        for key in new_values: 
            if key != 'file':
                v = str(key)
                r = re.compile(r"("+v+")=(\d*)")
          
                for line in fileinput.input([log_file], inplace=True):
                    # Search the current value for  new_values[key]
                    newV = new_values[key]
                    print r.sub(r"\1=%s"%newV,line.strip()) 
                 
  
    else:
        print 'No Parameters to Update'

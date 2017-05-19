import sys 
import os

f  = "/home/pi/fireball_camera/log_files/" + sys.argv[1]
 
if os.path.isfile(f):
    os.remove(f)
    
print "Log deleted"
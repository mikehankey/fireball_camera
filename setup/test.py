from __future__ import print_function
from datetime  import datetime
from subprocess import call
import subprocess
import os.path
import json


# Stop & Restart the APP
#sp = subprocess.Popen(['sudo','killall','node'])
#print('Node killed');
#sp.wait();
#sp = subprocess.Popen(['sudo','killall','forever'])
#print('Forever killed');
#sp.wait();
sp = subprocess.Popen(['sudo','forever','restartall'])
sp.wait();
print('AMSCam Launched');

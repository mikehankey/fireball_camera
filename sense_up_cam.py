#!/usr/bin/python3
import requests
import sys
from amscommon import read_config
cam_num = sys.argv[1]

config = read_config("conf/config-" + cam_num + ".txt")
r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=25&paramstep=0&paramreserved=0&")


import requests
import sys
api_key = "APIKEYHERE!"

# usage: python logger.py type msg
# type = type of log message (reboot, system, capture, calibration) 
# msg = log message 


type = sys.argv[1]
msg = sys.argv[2]

r = requests.post('http://localhost/test.php', data={'api_key': api_key, 'type': type, 'msg': msg})
print r.text

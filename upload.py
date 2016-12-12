import requests
import sys
api_key = "APIKEYHERE!"
# usage: python upload.py type filename 
# type = video
# type = starfield
# type = keyframes

# frame_data = list of x,y,pixel count for object on per frame basis for entire video (199 rows)
# event_starttime
# event_endtime

file = sys.argv[1]
type = sys.argv[2]
event_starttime = sys.argv[3]
event_endtime = sys.argv[4]
frame_data = "";

r = requests.post('http://localhost/test.php', data={'api_key': api_key, 'type': type, 'event_starttime': event_starttime, 'event_endtime': event_endtime, 'frame_data': frame_data}, files={'file_data': open(file, 'rb')})
print r.text

#!/usr/bin/python3
import ephem
import datetime
import sys
import glob

date = sys.argv[1]
cam_num = sys.argv[2]

path = "ffvids/" + cam_num + "/time_lapse"

somewhere = ephem.Observer()
somewhere.lat = '39' # <== change me
somewhere.lon = '-76' # <== and change me
somewhere.elevation = 112
somewhere.date = date + " 12:00:00"
print (somewhere.date)
sun = ephem.Sun()

r1 = somewhere.next_rising(sun)
s1 = somewhere.next_setting(sun)

somewhere.horizon = '-0:34'

r2 = somewhere.next_rising(sun)
s2 = somewhere.next_setting(sun)

start_date = datetime.datetime.strptime(str(s2), "%Y/%m/%d %H:%M:%S")
end_date = datetime.datetime.strptime(str(r2), "%Y/%m/%d %H:%M:%S")

print ("get files from sunset %s" % s1)
print(start_date)
print ("to sunrise %s" % r1)
print(end_date)

#print ("Naval obs sunrise %s" % r2)
#print ("Naval obs sunset %s" % s2)
file_list = []
for filename in (glob.glob(path + '/*.jpg')):
    el = filename.split("/")
    file = el[-1] 
    file_date = datetime.datetime.strptime(str(file), "capture-%Y-%m-%d_%H-%M-%S-stack.jpg")
    if start_date < file_date < end_date:
       file_list.append(filename)

sorted_list = sorted(file_list)

for filename in sorted_list:
   print(filename)

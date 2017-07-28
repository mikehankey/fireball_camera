#!/usr/bin/python
import sys
import Adafruit_DHT
import os
import glob
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
   f = open(device_file, 'r')
   lines = f.readlines()
   f.close()
   return lines

def read_temp():
   lines = read_temp_raw()
   while lines[0].strip()[-3:] != 'YES':
      time.sleep(0.2)
      lines = read_temp_raw()
   equals_pos = lines[1].find('t=')
   if equals_pos != -1:
      temp_string = lines[1][equals_pos+2:]
      temp_c = float(temp_string) / 1000.0
      temp_f = temp_c * 9.0 / 5.0 + 32.0
      return temp_c, temp_f

cooler_on = 0
while True:
   outside_temp_c, outside_temp_f = read_temp()
   humidity, inside_temp = Adafruit_DHT.read_retry(11, '24')
   diff = float(inside_temp) - float(outside_temp_c)
   print ("Outside Temp:", outside_temp_c)
   print ("Inside Temp:", inside_temp)
   print ("Temp Diff:", diff)
   print ("Humidity:", humidity)
   if (diff > 10 and cooler_on == 0):
      # turn cooler on if it's not already on
      cooler_on = 1
      os.system("/home/pi/fireball_camera/pizero-relay.py cooler_on 1");
   else: 
      # turn cooler off if it's already on
      cooler_on = 0
      os.system("/home/pi/fireball_camera/pizero-relay.py cooler_off 1");
   time.sleep(1)







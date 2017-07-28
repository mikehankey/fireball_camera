#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import sys
# ALLSKY6 CAM & CLIMATE MODULE 
# PIZERO GPIO BOARD PIN MAPPING
# For Switch
# cams
# 1 - 40
# 2 - 38
# 3 - 36
# 4 - 37
# 5 - 35
# 6 - 13
# cooler/fan
# 7 - 11 # cooler 
# 8 - 15 # fan

# For Temp Sensors
# Outside - 16
# Insider - 18
cooler = {}
cams = {}
cams[1] = 40
cams[2] = 38
cams[3] = 36
cams[4] = 37
cams[5] = 35
cams[6] = 13
cooler[1] = 11
cooler[2] = 15

def all_on(delay = 5):
   for x in range (1,len(cams)+1):
      print ("setting up: ", x)
      GPIO.setup(cams[x], GPIO.OUT)

   print ("ON", cams[1])
   cam_on_off(1, "ON")
   time.sleep(delay)
   cam_on_off(2, "ON")
   time.sleep(delay)
   cam_on_off(3, "ON")
   time.sleep(delay)
   cam_on_off(4, "ON")
   time.sleep(delay)
   cam_on_off(5, "ON")
   time.sleep(delay)
   cam_on_off(6, "ON")
   time.sleep(delay)
   cooler_on_off(1, "ON")
   time.sleep(delay)
   cooler_on_off(2, "ON")
   time.sleep(delay)

def all_off():
   cam_on_off(1, "OFF")
   cam_on_off(2, "OFF")
   cam_on_off(3, "OFF")
   cam_on_off(4, "OFF")
   cam_on_off(5, "OFF")
   cam_on_off(6, "OFF")
   cooler_on_off(1, "OFF")
   cooler_on_off(2, "OFF")

def cam_on_off(cam, signal):
   GPIO.setup(cams[cam], GPIO.OUT)
   if signal == 'ON':
      GPIO.output(cams[cam], GPIO.LOW)
   if signal == 'OFF':
      GPIO.output(cams[cam], GPIO.HIGH)

def cooler_on_off(cool, signal):
   GPIO.setup(cooler[cool], GPIO.OUT)
   if signal == 'ON':
      GPIO.output(cooler[cool], GPIO.LOW)
   if signal == 'OFF':
      GPIO.output(cooler[cool], GPIO.HIGH)

   

GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)

cmd = sys.argv[1]

if cmd == 'all_on':
   delay = int(sys.argv[2])
   all_on(delay)

if cmd == 'all_off':
   all_off()

if cmd == 'cam_on':
   cam = int(sys.argv[2])
   cam_on_off(cam, "ON")
if cmd == 'cam_off':
   cam = int(sys.argv[2])
   cam_on_off(cam, "OFF")

if cmd == 'cooler_on':
   cool = int(sys.argv[2])
   cam_on_off(cool, "ON")
if cmd == 'cooler_off':
   cool = int(sys.argv[2])
   cam_on_off(cool, "OFF")


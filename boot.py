#!/usr/bin/python3 

# system boot script runs each time system is booted. 
# Handles first time registration and setup
# once setup simply does sanity check and logs to ams 

fp = open("/home/pi/fireball_camera/booted.txt", "w")
fp.write("booted")
fp.close()

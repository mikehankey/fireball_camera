#!/bin/bash


procount=$(ps -aux | grep capture-hd.py |grep -v grep| wc -l);
if [[ $procount -eq 6 ]]; then
     echo 1
elif [[ $procount -eq 5 ]]; then
     echo 1
else
     echo 0
     /home/pi/fireball_camera/capture-stop.sh
fi


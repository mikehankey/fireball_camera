#!/bin/bash


procount=$(ps -aux | grep capture.py |grep -v grep| wc -l);
echo $procount
if [[ $procount -eq 4 ]]; then
     echo "Capture Processes Running"
elif [[ $procount -eq 3 ]]; then
     echo "Capture Processes Running..."
else
     echo "Capture Processes NOT Running. Starting...";
     /home/pi/capture/capture-stop.sh
     sleep 5
     /home/pi/capture/capture-start.sh
fi

echo "check defunct"
defunct=$(ps -aux | grep python3 |grep defunct| wc -l);
echo $defunct
if [[ $defunct -eq 1 ]]; then
     echo "Capture Processes Defunct. Restarting..."
     /home/pi/capture/capture-stop.sh
     sleep 5
     /home/pi/capture/capture-start.sh
fi


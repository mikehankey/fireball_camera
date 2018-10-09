#!/usr/bin/python3

import os
import requests
import datetime
import time
import cv2
import numpy as np
import sys

def cam_loop(cam_ip):
    cv2.namedWindow("pepe")
    config = {}
    config['cam_ip'] = cam_ip
    print (config['cam_ip'])

    cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1&user=admin&password=admin")

    image_acc = None

    time.sleep(5)
    while True:
        _ , frame = cap.read()
        if frame is not None:
           cv2.imshow('pepe', frame)
           cv2.waitKey(1)
cam_ip = sys.argv[1]

cam_loop(cam_ip)

#!/usr/bin/python3
#from subprocess import call
import os
import requests
from collections import deque
#from queue import Queue
import multiprocessing
#from multiprocessing import Process, Manager
import datetime
import cv2
import numpy as np
import iproc 
import time
import syslog
import sys
MORPH_KERNEL = np.ones((10, 10), np.uint8)
record = 1

def cam_loop(pipe_parent, shared_dict):
    lc = 0
    tstamp_prev = None
    motion_on = 0
    motion_off = 0
    config = read_config()
    print (config['cam_ip'])
    print (config['hd'])
    if int(config['hd']) == 1:
        print ("capture_hd")
        cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_0&user=admin&password=admin&tcp")
        resize = .25
    else:
        cap = cv2.VideoCapture("rtsp://" + config['cam_ip'] + "/av0_1&user=admin&password=admin&tcp")
        resize = .5

    cv2.setUseOptimized(True)
    image_acc = None

    time.sleep(5)
    frames = deque(maxlen=200)
    frame_times = deque(maxlen=200)
    time_start = datetime.datetime.now()
    count = 0

    while True:
        _ , frame = cap.read()
        if _ is True:
            frame_time = datetime.datetime.now()
            frames.appendleft(frame)
            frame_times.appendleft(frame_time)
        if count % 3 == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            pipe_parent.send(cv2.resize(frame, (0,0), fx=resize, fy=resize))

        if count % 100 == 0:
            time_diff = frame_time - time_start
            fps = count / time_diff.total_seconds()
            print("FPS: " + str(fps))
            count = 1
            lc = lc + 1
            print ("LC:" + str(lc))
            time_start = frame_time
        if lc < 5:
            shared_dict['motion_on'] = 0
            shared_dict['motion_off'] = 0 
  

      # check the lock, if it exists we need to dump the buffer
        mmo= shared_dict['motion_on']; 
        mmof= shared_dict['motion_off']; 

        print("MMO:", mmo, mmof)

        if (mmo >= 5 and mmof >= 15 and lc > 4):
            #r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=25&paramstep=0&paramreserved=0&")

            #r = requests.get("http://" + config['cam_ip'] + "/webs/btnSettingEx?flag=1000&paramchannel=0&paramcmd=1058&paramctrl=50&paramstep=0&paramreserved=0&")
            print("RECORD BUFFER NOW!\n")
            shared_dict['motion_on'] = 0
            shared_dict['motion_off'] = 0 
            mmo = 0
            mmof = 0
            lc = 0
            format_time = frame_time.strftime("%Y%m%d%H%M%S")
            outfile = "{}/{}.avi".format("/var/www/html/out", format_time)
            outfile_text = "{}/{}.txt".format("/var/www/html/out", format_time) 

            df = open(outfile_text, 'w', 1)
            dql = len(frame_times) - 2
            print (dql)
            time_diff = frame_times[1] - frame_times[dql]
            if time_diff.total_seconds() > 0:
                fps = 200 / time_diff.total_seconds()
            else: 
                fps = 20
            print ("FPS: ", fps)
            writer = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*'MJPG'), fps, (frames[0].shape[1], frames[0].shape[0]), True)
            while frames:
                img = frames.pop()
                ft = frame_times.pop()
                format_time = ft.strftime("%Y-%m-%d %H:%M:%S.")
                dec_sec = ft.strftime("%f")
                format_time = format_time + dec_sec
                df.write(format_time +"\n")
                writer.write(img)
                   #i = i + 1
            writer.release()
            df.close()
        count = count + 1

 
def show_loop(pipe_child, shared_dict):
    #cv2.namedWindow("pepe")
    config = read_config()
    print (config['cam_ip'])

    cam_lat = config['cam_lat']
    cam_lon = config['cam_lon']
    cam_operator = config['cam_operator']
    cam_id= config['cam_id']

    image_acc = None
    nice_image_acc = None
    tstamp_prev = None
    count = 0
    #time_start = datetime.datetime.now()
    time_start = time.time()
    frame = pipe_child.recv()
    frames = deque(maxlen=200)
    frame_times = deque(maxlen=200)
    frame_data = deque(maxlen=200)

    motion_on = 0
    motion_off = 0
    cnts = []
    lc = 1
    calibrate_now = 0
    calibrate_start = 0
    #sense_up = 0
 
    while True:
        frame = pipe_child.recv()
        alpha, tstamp_prev = iproc.getAlpha(tstamp_prev)
        #lock.acquire()
        #print ("SHOW LOOP:", count)

        #frame = cv2.resize(frame, (0,0), fx=0.8, fy=0.8)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
        if image_acc is None:
            image_acc = np.empty(np.shape(frame))
        image_diff = cv2.absdiff(image_acc.astype(frame.dtype), frame,)
        hello = cv2.accumulateWeighted(frame, image_acc, alpha)


        _, threshold = cv2.threshold(image_diff, 30, 255, cv2.THRESH_BINARY)
        thresh= cv2.dilate(threshold, None , iterations=2)
        (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #print(len(cnts), motion_on, motion_off)
        #print(cnts)
        if len(cnts) == 0:
            shared_dict['motion_off'] = shared_dict['motion_off'] + 1
        else:
            shared_dict['motion_on'] = shared_dict['motion_on'] + 1
            shared_dict['motion_off'] = 0 
        if shared_dict['motion_off'] > 5 and shared_dict['motion_on'] < 3:
            shared_dict['motion_on'] = 0
        #cv2.imshow('pepe', image_diff)
        #cv2.waitKey(5)
        count = count + 1
        #shared_dict['motion_on'] = motion_on
        #shared_dict['motion_off'] = motion_off

def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
      #print key, value
    return(config)




 
def write_buffer(frames):
    print ("YA, write")
    for i in range(len(frames), 0, -1):
         print (i)
         frames[i-0]



if __name__ == '__main__':
 
    print ("Capture Program")
    #logger = multiprocessing.log_to_stderr()
    #logger.setLevel(multiprocessing.SUBDEBUG)
 
    pipe_parent, pipe_child = multiprocessing.Pipe()
    man = multiprocessing.Manager()

    shared_dict = man.dict()
    shared_dict['motion_on'] = 0; 
    shared_dict['motion_off'] = 0; 


    cam_process = multiprocessing.Process(target=cam_loop,args=(pipe_parent, shared_dict))
    cam_process.start()
 
    show_process = multiprocessing.Process(target=show_loop,args=(pipe_child, shared_dict))
    show_process.start()

    cam_process.join()
    show_loop.join()

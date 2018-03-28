#!/usr/bin/python3
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from random import randint
import time
import ephem
from PIL import Image
import cv2
import glob
import sys
import os
import numpy as np
import datetime
from pathlib import Path
import subprocess
from amscommon import read_config
import math
import time
from sklearn.cluster import Birch
from collections import deque

video_dir = "/mnt/ams2/SD/"


def cluster(points):
   brc = Birch(branching_factor=50, n_clusters=3, threshold=.5, compute_labels=True)
   print(brc.fit(points))
   Birch(branching_factor=50, compute_labels=True, copy=True, n_clusters=3, threshold=.5, )
   #return(brc.predict(points))
   return(brc.fit(points))

 

def calc_dist(x1,y1,x2,y2):  
   dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
   return dist  


def find_angle(x1,x2,y1,y2):
   if x2 - x1 != 0:
      a1 = (y2 - y1) / (x2 - x1)
   else:
      a1 = 0
   angle = math.atan(a1)

   angle = math.degrees(angle)
   return(angle)

def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]

def find_objects(index, points):
   apoints = []
   unused_points = []
   cl_sort = []
   sorted_points = []
   last_angle = None
   objects = []
   group_pts = []
   line_segments = []
   count = 0
   x1,y1,w1,h1 = points[index]
   print ("Total Points found in image: ", len(points))
   used_pts = {}
   for i in range(0,len(points)-1):
      x1,y1,w1,h1 = points[i] 
      for i in range(0,len(points)-1):
         x2,y2,w2,h2 = points[i] 
         key = str(x1)+"."+str(y1)+"."+str(x2)+"."+str(y2)
         used_pts[key] = 0
         key2 = str(x2)+"."+str(y2)+"."+str(x1)+"."+str(y1)
         used_pts[key2] = 0


   for i in range(0,len(points)-1):
      closest = []
      x1,y1,w1,h1 = points[i] 
      for j in range(0,len(points)-1):
         x2,y2,w2,h2 = points[j]
         key = str(x1)+"."+str(y1)+"."+str(x2)+"."+str(y2)
         key2 = str(x2)+"."+str(y2)+"."+str(x1)+"."+str(y1)
         dist = calc_dist(x1,y1,x2,y2)
         angle = find_angle(x1,y1,x2,y2)
         if x1 != x2 and y1 != y2:
            if used_pts[key] == 0 and used_pts[key2] == 0:
               #print("Closest Point:", (int(dist),int(angle),int(x1),int(y1),int(x2),int(y2)))
               closest.append((int(dist),int(angle),int(x1),int(y1),int(x2),int(y2)))

               used_pts[key] = 1
               used_pts[key2] = 1 
               #print("Key has been used:", key, key2)
            #else:
            #   print("Key already used try another one:", key, key2)

            #else:
            #   print ("this point has already been used")
         count = count + 1
      # find the closest point and make a line segment and add that to the line segments list
      if len(closest) > 0:
         distsort = np.unique(closest, axis=0)
         dist,angle,x1,y1,x2,y2 = distsort[0]
         if dist < 50:
            line_segments.append((int(dist),int(angle),int(x1),int(y1),int(x2),int(y2)))
         
         #print("CLOSEST LINE SEGMENT FOR PT: ", distsort[0])
      else: 
         print("ERROR! no close points to this one!", x1,y1)
      if w1 > 10 or h1 > 10:
         print ("BIG!!! We have a big object here likely containing many line segments.")
   #print ("OBJECT POINTS")
   if len(line_segments) > 0:
      sorted_lines = sorted(line_segments, key=lambda x: x[2])
   else: 
      sorted_lines = []

   #print ("LINE SEGMENTS:")
   #for line in sorted_lines:
   #   print (line) 

   last_ang = 0
   last_dist = 0
   line_groups = []
   line_group = []
   orphan_lines = []
   if len(sorted_lines) > 0:
      for segment in sorted_lines:
         dist,angle,x1,y1,x2,y2 = segment
         if last_ang != 0 and (angle -5 < last_ang < angle + 5) and dist < 100:
            #print ("Line Segment Part of Existing Group: ", segment)
            line_group.append((dist,angle,x1,y1,x2,y2))
         else:
            #print ("New Group Started!", last_ang, angle )
            #   print ("Line Segment Part of New Group: ", segment)
            if len(line_group) >= 3:
               line_groups.append(line_group)
            else: 
               #print("Last line segment was too small to be part of a group! These are random points or stars. Skip for now.")
               for line in line_group:
                  orphan_lines.append(line)
         
            line_group = []
            line_group.append((dist,angle,x1,y1,x2,y2))
         last_ang = angle
   if len(line_group) == 2:
      # make sure these two groups are close enough to each other to be grouped. 
      (dist,angle,x1,y1,x2,y2) = line_group[0]
      (xdist,xangle,xx1,xy1,xx2,xy2) = line_group[1]
     


   if len(line_group) >= 2:
      line_groups.append(line_group)
   else:
      for line in line_group:
         orphan_lines.append(line)

   # now make sure all of the line segments in the line group can connect to at least one of the other segments
   #print ("Total Line Groups as of now:", len(line_groups))
   #print ("Total Orphan Lines as of now:", len(orphan_lines))

   #print ("Confirm the line segments are all part of the same group", len(line_groups))


   print ("TOTAL POINTS: ", len(points))
   print ("TOTAL LINE GROUPS: ", len(line_groups))
   print ("ORPHAN GROUPS: ", len(orphan_lines))

   gc = 1
   if len(line_groups) > 0:
      for line_group in line_groups:
         lc = 1
         for line in line_group:
            dist,ang,x1,y1,x2,y2 = line
            #confirm_angle = find_angle(x1,y1,x2,y2)
            #print ("GROUP", gc, lc, line, ang, confirm_angle) 
            lc = lc + 1
         gc = gc + 1
   #else:
   #   for point in points:
   #      print ("POINT: ", point)
 
   return(line_groups, orphan_lines)

def confirm_cnts(crop):
   crop = cv2.GaussianBlur(crop, (5, 5), 0)
   avg_flux = np.average(crop)
   max_flux = np.amax(crop)
   thresh_limit = avg_flux / 2 
   _, crop_thresh = cv2.threshold(crop, thresh_limit, 255, cv2.THRESH_BINARY)

   #(_, cnts, xx) = cv2.findContours(crop_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


   #if np.sum(crop_thresh) > (255 * 2):
      #print ("CONFIRM:", max_flux, avg_flux, thresh_limit, np.sum(crop_thresh))
      #cv2.imshow('pepe', crop_thresh)
   #else:
   #   print ("FAILED:", max_flux, avg_flux, thresh_limit, np.sum(crop_thresh))
      #cv2.imshow('pepe', crop)
   #cv2.waitKey(100)
   return(np.sum(crop_thresh)) 

def find_best_thresh(image, thresh_limit):
   go = 1
   while go == 1: 
      _, thresh = cv2.threshold(image, thresh_limit, 255, cv2.THRESH_BINARY)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      if len(cnts) > 45:
         thresh_limit = thresh_limit + 2
      else: 
         go = 0
      print ("BEST THRESH:", thresh_limit)
   return(thresh_limit)


def find_objects2(timage, tag, current_image, filename):
   image = timage
   thresh_limit = 25 
   thresh_limit = find_best_thresh(image, thresh_limit)
   # find best thresh limit code here!
   line_objects = []
   points = []
   orphan_lines = []
   _, thresh = cv2.threshold(image, thresh_limit, 255, cv2.THRESH_BINARY)
   (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   print ("CNTS:", len(cnts))
   hit = 0
   objects = []
   if len(cnts) < 500:
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         if w > 1 and h > 1:
            if (w < 25 and h <25):
               nothing = 0
              # cv2.rectangle(image, (x,y), (x+w+5, y+h+5), (255),1)
               #cv2.circle(image, (x,y), 20, (120), 1)
               #if w != h:
               #   cv2.rectangle(image, (x,y), (x+w+5, y+h+5), (255),1)
            else:
               #cv2.rectangle(image, (x,y), (x+w+5, y+h+5), (255),1)
               # Convert big object into points and add each one to the points array. 
               crop = timage[y:y+h,x:x+w]
               points.append((x,y,w,h))
               if w < 600 and h < 400:
                  crop_points = find_points_in_crop(crop,x,y,w,h)
                  for x,y,w,h in crop_points:
                  #print("adding some points",x,y,w,h)
                     points.append((x,y,w,h))
      

            points.append((x,y,w,h))
            #objects.append((x,y,w,h))
         else:
            image[y:y+h,x:x+w] = [0]
   else: 
      print ("WAY TO MANY CNTS:", len(cnts))
      thresh_limit = thresh_limit + 5

   # find line objects
   if (len(objects) + len(points)) > 0:
      line_groups, orphan_lines = find_objects(0, points)
   else:
      line_groups = []

   final_group = []
   final_groups = []
   reject_group = []
   reject_groups = []

   line_segments = flatten_line_groups(line_groups)
   line_segments = sorted(line_segments, key = lambda x: (x[0],x[1]))

   if len(line_segments) > 0:
      final_group, reject_group = regroup_lines(line_segments)
      print ("MIKE!:", len(final_group))
      if len(final_group) > 1:
         final_groups.append(final_group)
      else: 
         for line in final_group:
            orphan_lines.append(line)
   if len(reject_group) > 3:
      print (len(reject_group), "rejects left. do it again.")
      reject_group = sorted(reject_group, key = lambda x: (x[1],x[0]))

      final_group, reject_group = regroup_lines(reject_group)
      if len(final_group) > 1:
         final_groups.append(final_group)
      else: 
         for line in final_group:
            orphan_lines.append(line)

      print (len(reject_group), "rejects left after 2nd try")
   if len(reject_group) > 3:
      print (len(reject_group), "rejects left. do it again.")
      final_group, reject_group = regroup_lines(reject_group)
      if len(final_group) > 1:
         final_groups.append(final_group)
      else: 
         for line in final_group:
            orphan_lines.append(line)
      print (len(reject_group), "rejects left after 3rd try")

   # try to adopt the orphans! 
   if len(orphan_lines) >= 1:
      print (orphan_lines)
      final_group, reject_group = regroup_lines(orphan_lines)
      if len(final_group) > 1:
         final_groups.append(final_group)
      if len(final_group) > 0:
         print ("Adopted! : ", final_group)
      orphan_lines = reject_group

   print ("FINAL ANALYSIS")
   print (final_groups)
   print ("--------------")
   print ("File Name: ", filename)
   print ("Total Points:", len(points))
   print ("Total Line Segments:", len(line_segments))
   print ("Total Final Line Groups:", len(final_groups))
   print (final_groups)
   print ("Total Rejected Lines:", len(reject_group))
   gc = 1
   xs = ys = []
   for line_group in final_groups: 
      lc = 1
      for line in line_group:
         dist,angle,x1,y1,x2,y2 = line
         xs.append(x1) 
         xs.append(x2) 
         ys.append(y1) 
         ys.append(y2) 
         print (gc, lc, line)    
         lc = lc + 1
      gc = gc + 1

   if len(xs) > 0 and len(ys) > 0:
      mnx = min(xs)
      mxx = max(xs)
      mny = min(ys)
      mxy = max(ys)
      cv2.rectangle(image, (mnx,mny), (mxx, mxy), (255),1)

   print ("Total Orphaned Lines:", len(orphan_lines))

   if len(line_groups) > 0:
      line_segments = flatten_line_groups(line_groups) 
      find_line_nodes(line_segments)
      gc = 1
      for line_group in line_groups:
         lc = 1
         line_group = sorted(line_group, key = lambda x: (x[2],x[3]))
         dist,angle,sx1,sy1,sx2,sy2 = line_group[0]
         for line in line_group:
            dist,angle,x1,y1,x2,y2 = line
            #s_ang = find_angle(sx1,sy1,x1,y1)
            #if angle - 5 < s_ang < angle + 5:
            #   print("FINAL GROUP:", gc,lc,line, angle, s_ang)
            #   final_group.append((dist,angle,x1,y1,x2,y2))
            #else:
            #   print("REJECT GROUP:", gc,lc,line, angle, s_ang)
            #   reject_group.append((dist,angle,x1,y1,x2,y2))
            #seg_dist = find_closest_segment(line, line_group)
            cv2.line(image, (x1,y1), (x2,y2), (255), 2)    
            cv2.putText(image, "L " + str(lc),  (x1+25,y1+10), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
            lc = lc + 1
         if len(line_group) > 0:
            cv2.putText(image, "LG " + str(gc),  (x1+25,y1), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
         gc = gc + 1
            

   for line in orphan_lines:
      print("ORPHAN:", line)
      dist,angle,x1,y1,x2,y2 = line
      cv2.line(image, (x1,y1), (x2,y2), (255), 1)    
      cv2.putText(image, "Orph" ,  (x1+25,y1), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)


         #cv2.ellipse(image,(ax,ay),(dist_x,dist_y),elp_ang,elp_ang,180,255,-1)  
         #a,b = best_fit(lxs, lys)         
         #plt.scatter(lxs,lys)
         #plt.xlim(0,640)
         #plt.ylim(0,480)
         #yfit = [a + b * xi for xi in lxs]
         #plt.plot(lxs,yfit)
         #cv2.imshow('pepe', image)
         #cv2.waitKey(1)
         #plt.gca().invert_yaxis()
         #plt.show()


   for x,y,w,h in points:
      if w > 25 or h > 25:
         cv2.rectangle(image, (x,y), (x+w+5, y+h+5), (255),1)
      else:
         cv2.circle(image, (x,y), 20, (120), 1)

   edges = cv2.Canny(image.copy(),thresh_limit,255)
   el = filename.split("/");
   fn = el[-1]
   cv2.putText(current_image, "File Name: " + fn,  (10,440), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   cv2.putText(current_image, str(tag),  (10,450), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   cv2.putText(current_image, "Points: " + str(len(points)),  (10,460), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   cv2.putText(current_image, "Line Groups: " + str(len(final_groups)),  (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   blend = cv2.addWeighted(image, .2, current_image, .8,0)
   cv2.imshow('pepe', blend)
   if len(final_groups) >= 1:
      while(1):
         k = cv2.waitKey(33)
         if k == 32:
            break 
         if k == 27:
            exit() 
   else:
      cv2.waitKey(100)
   #exit()
   return(line_groups, points)

def regroup_lines(line_segments):
   final_group = []
   reject_group = []

   sangles = []
   dist,angle,sx1,sy1,sx2,sy2 = line_segments[0]
   for line in line_segments:
      dist,angle,x1,y1,x2,y2 = line
      s_ang = find_angle(sx1,sy1,x1,y1)
      sangles.append(s_ang)
   mean_angle = np.median(np.array(sangles))

   if len(line_segments ) > 0:
      dist,angle,sx1,sy1,sx2,sy2 = line_segments[0]
      for line in line_segments:
         dist,angle,x1,y1,x2,y2 = line
         s_ang = find_angle(sx1,sy1,x1,y1)
         if mean_angle - 10 <= s_ang <= mean_angle + 10:
            print("FINAL GROUP:", line, angle, s_ang, mean_angle)
            final_group.append((dist,angle,x1,y1,x2,y2))
         else:
            print("REJECT GROUP:",line, angle, s_ang, mean_angle)
            reject_group.append((dist,angle,x1,y1,x2,y2))
   return(final_group, reject_group)

def flatten_line_groups(line_groups):
   line_segments = []
   for line_group in line_groups:
      for line in line_group:
         dist,angle,x1,y1,x2,y2 = line
         line_segments.append((dist,angle,x1,y1,x2,y2))
   return(line_segments)

def log_node(nodes, line, closest):
   if len(nodes) == 0: 
      nodes.append((line,closest))   

   return(nodes)

def find_line_nodes(line_segments):
   nodes = [] 
   seg_list = [] 
   rest = line_segments
   for line in line_segments:
      #print("LENLINE", len(line))
      #print(line)
      dist,angle,x1,y1,x2,y2 = line 
      closest, rest = sort_segs(x1,y1,rest)
      #nodes = log_node(nodes, line, closest)

def sort_segs(x,y,seg_dist):
   sorted_lines = sorted(seg_dist, key=lambda x: x[0])
   
   #for line in sorted_lines:
   #   print ("SORTED LINE", line)
   closest = []
   rest = []
   already_found = 0
   for line in sorted_lines:
      if len(line) == 6:
         dist,angle,x1,y1,x2,y2 = line
      else: 
         print("WTF!:", line)
      seg_dist = calc_dist(x,y,x1,y1)
      if seg_dist != 0 and already_found != 1:
         closest.append((dist,angle,x1,y1,x2,y2))
      else:
         rest.append((dist,angle,x1,y1,x2,y2))

   return(closest, rest)
      
      


def find_closest_segment(this_line,line_group):
   seg_dist = []
   dist, angle, x1,y1,x2,y2 = this_line
   cx = (x1 + x2) / 2
   cy = (y1 + y2) / 2
   for line in line_group:
      xdist, xangle, xx1,xy1,xx2,xy2 = line
      xcx = (xx1 + xx2) / 2
      xcy = (xy1 + xy2) / 2
      dist = calc_dist(cx,cy,xcx,xcy)
      if dist > 0:
         seg_dist.append((dist, x1,y1,x2,y2))

   sorted_lines = sorted(seg_dist, key=lambda x: x[0])
   #for line in sorted_lines:
   #   print("CLOSEST SEGMENTS:", line)


def find_points_in_crop(crop,x,y,w,h):
   print ("cropping")
   go = 1
   cnt_pts = []
   thresh_limit = 250 

   canvas = np.zeros([480,640], dtype=crop.dtype)
   canvas[y:y+h,x:x+w] = crop
   for i in range(x,x+w):
      for j in range(y,y+w): 
         if i % 10 == 0:
            canvas[0:480,i:i+5] = 0
         if j % 10 == 0:
            canvas[j:j+5,0:640] = 0
   print ("CROP", crop.shape[0])
   if crop.shape[0] > 25:
      cv2.imshow('pepe', canvas)
      cv2.waitKey(1000)
            


   while go == 1:
     _, thresh = cv2.threshold(canvas, thresh_limit, 255, cv2.THRESH_BINARY)
     (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

     cnt_limit = int((w + h) / 20)
     if cnt_limit < 5:
        cnt_limit = 5
     if cnt_limit > 10:
        cnt_limit = 10
     #print ("CNTS at thresh:", len(cnts), thresh_limit)
     thresh_limit = thresh_limit - 2
     if len(cnts) >= cnt_limit:
        for (i,c) in enumerate(cnts):
           x,y,w,h = cv2.boundingRect(cnts[i])
           if w > 1 and h > 1:
              cnt_pts.append((x,y,w,h))
        go = 0
     if thresh_limit < 10:
        go = 0
     #cv2.imshow('pepe', thresh)
     #cv2.waitKey(100)

   return(cnt_pts) 


def best_fit(X, Y):

    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b


def diff_all(med_stack_all, background, median, before_image, current_image, after_image,filename ):

   before_diff = cv2.absdiff(current_image.astype(current_image.dtype), before_image,)
   after_diff = cv2.absdiff(current_image.astype(current_image.dtype), after_image,)
   before_after_diff = cv2.absdiff(before_image.astype(current_image.dtype), after_image,)

   median_three = np.median(np.array((before_image, after_image, current_image)), axis=0)
   median = np.uint8(median)
   median_sum = np.sum(median)

   median_diff = cv2.absdiff(median_three.astype(current_image.dtype), median,)

   blur_med = cv2.GaussianBlur(median, (5, 5), 0)

   # find bright areas in median and mask them out of the current image
   _, median_thresh = cv2.threshold(blur_med, 40, 255, cv2.THRESH_BINARY)

   (_, cnts, xx) = cv2.findContours(median_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   hit = 0
   real_cnts = []
   if len(cnts) < 1000:
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         if True:
            w = w + 5 
            h = h + 5 
            x = x - 5
            y = y - 5
            if x < 0: 
               x = 0
            if y < 0: 
               y = 0
            if x+w > current_image.shape[1]: 
               x = current_image.shape[1]-1
            if y+h > current_image.shape[0]: 
               y = current_image.shape[0]-1
         if w > 0 and h > 0:
            mask = current_image[y:y+h, x:x+w]
            #cv2.rectangle(current_image, (x,y), (x+w+5, y+h+5), (255),1)
            for xx in range(0, mask.shape[1]):
               for yy in range(0, mask.shape[0]):
                  mask[yy,xx] = randint(0,6)
            blur_mask = cv2.GaussianBlur(mask, (5, 5), 0)
            current_image[y:y+h,x:x+w] =blur_mask 
            median[y:y+h,x:x+w] =mask 

   # find the diff between the masked median and the masked current image
   blur_cur = cv2.GaussianBlur(current_image, (5, 5), 0)
   blur_med = cv2.GaussianBlur(median, (5, 5), 0)
   cur_med_diff = cv2.absdiff(blur_cur.astype(blur_cur.dtype), blur_med,)

   blend = cv2.addWeighted(current_image, .5, cur_med_diff, .5,0)

   cur_med_diff =- median

   line_groups, points = find_objects2(blend, "Current Median Diff Blend",  current_image, filename)

   return(line_groups, points)

def inspect_image(med_stack_all, background, median, before_image, current_image, after_image, avg_cnt,avg_tot,avg_pts,filename):
   rois = []
   image_diff = cv2.absdiff(current_image.astype(current_image.dtype), background,)
   orig_image = current_image
   current_image = image_diff
   line_groups, points = diff_all(med_stack_all, background, median, before_image, current_image, after_image,filename)
   if len(line_groups) >= 1:
      return(1, line_groups, points)
   else:
      return(0,line_groups, points)


def parse_file_date(orig_video_file):
   #print(orig_video_file)
   if ".mp4" in orig_video_file:
      stacked_image_fn = orig_video_file.replace(".mp4", "-stack.jpg") 
      star_image_fn = orig_video_file.replace(".mp4", "-stars.jpg")
      report_fn = orig_video_file.replace(".mp4", "-report.txt")

      trim_file = orig_video_file.replace(".mp4", "-trim.mp4")

   else:
      stacked_image_fn = orig_video_file.replace(".avi", "-stack.jpg") 
      trim_file = orig_video_file.replace(".avi", "-trim.avi")
      star_image_fn = orig_video_file.replace(".avi", "-stars.jpg")
      report_fn = orig_video_file.replace(".avi", "-report.txt")
      el = orig_video_file.split("/")
      file_name = el[-1]
      file_name = file_name.replace("_", "-")
      file_name = file_name.replace(".", "-")
      #print ("FN", file_name)
      xyear, xmonth, xday, xhour, xmin, xsec, xcam_num, ftype, xext = file_name.split("-")
      cam_num = xcam_num.replace("cam", "")

      date_str = xyear + "-" + xmonth + "-" + xday + " " + xhour + ":" + xmin + ":" + xsec
      capture_date = date_str
      return(capture_date)


def day_or_night(config, capture_date):

   obs = ephem.Observer()

   obs.pressure = 0
   obs.horizon = '-0:34'
   obs.lat = config['device_lat']
   obs.lon = config['device_lng']
   obs.date = capture_date

   sun = ephem.Sun()
   sun.compute(obs)

   (sun_alt, x,y) = str(sun.alt).split(":")

   saz = str(sun.az)
   (sun_az, x,y) = saz.split(":")
   #print ("SUN", sun_alt)
   if int(sun_alt) < -1:
      sun_status = "night"
   else:
      sun_status = "day"
   return(sun_status)

def diff_stills(sdate, cam_num):
   med_last_objects = []
   last_objects = deque(maxlen=5) 
   diffed_files = []
   config = read_config("conf/config-1.txt")
   video_dir = "/mnt/ams2/SD/"
   images = []
   count = 0
   last_image = None
   last_thresh_sum = 0
   hits = 0
   avg_cnt = 0
   avg_tot = 0
   avg_pts = 0
   count = 0

   glob_dir = video_dir + "proc/" + sdate + "/" + "*cam" + str(cam_num) + "-stacked.jpg"
   report_file = video_dir + "proc/" + sdate + "/" + sdate + "-cam" + str(cam_num) + "-report.txt"

   cv2.namedWindow('pepe')
   mask_file = "conf/mask-" + str(cam_num) + ".txt"
   file_exists = Path(mask_file)
   mask_exists = 0
   if (file_exists.is_file()):
      print("File found.")
      ms = open(mask_file)
      for lines in ms:
         line, jk = lines.split("\n")
         exec(line)
      ms.close()
      mask_exists = 1
      (sm_min_x, sm_max_x, sm_min_y, sm_max_y) = still_mask

   diffs = 0
   image_list = []
   file_list = []
   sorted_list = []
   print ("Loading still images from ", glob_dir)
   fp = open(report_file, "w")
   for filename in (glob.glob(glob_dir)):
       capture_date = parse_file_date(filename)
       sun_status = day_or_night(config, capture_date)
       if sun_status != 'day':
          #print("NIGHTTIME", capture_date, filename, sun_status)
          file_list.append(filename)
   
   sorted_list = sorted(file_list)
   for filename in sorted_list:
      open_cv_image = cv2.imread(filename,0)
      open_cv_image[440:480, 0:640] = [0]
      if mask_exists == 1:
         open_cv_image[sm_min_y:sm_max_y, sm_min_x:sm_max_x] = [0]
      images.append(open_cv_image)
   
   #exit()
   #time.sleep(5)
   height , width =  open_cv_image.shape
   
   # Define the codec and create VideoWriter object
   #fourcc = cv2.VideoWriter_fourcc(*'H264')
   #out = cv2.VideoWriter(outfile,fourcc, 5, (width,height),1)
   #med_stack_all = np.median(np.array(images[50:150]), axis=0)
   med_stack_all = np.median(np.array(images), axis=0)
   #cv2.imshow('pepe', cv2.convertScaleAbs(med_stack_all))
   #cv2.waitKey(1000)
   objects = None
   last_line_groups = []
   last_points = []
   for filename in sorted_list:
      hit = 0
      detect = 0
      el = filename.split("/")
      fn = el[-1]
      #this_image = cv2.imread(filename,1)
      this_image = images[count]
   
   
      if count >= 1:
         before_image = images[count-1]
      else:
         before_image = images[count+2]
   
      if count >= len(file_list)-1:
         after_image = images[count-2]
      else:
         after_image = images[count+1]
   
      if count < 25:
         median = np.median(np.array(images[0:count+25]), axis=0)
         
      elif len(images) - count < 25:
         median = np.median(np.array(images[count-25:count]), axis=0)
      else:
         median = np.median(np.array(images[count-25:count]), axis=0)


     
      if count < 10:
         background = images[count+1] 
         for i in range (0,10):
            background = cv2.addWeighted(background, .8, images[count+i], .2,0)
      else:
         background = images[count-1] 
         for i in range (0,10):
            background = cv2.addWeighted(background, .8, images[count-i], .2,0)
 
 

      result, line_groups, points = inspect_image(med_stack_all, background, median, before_image, this_image, after_image, avg_cnt,avg_tot,avg_pts, filename) 
      # block out the detections in the master image to remove it from the running mask
      last_line_group = line_groups
      last_points = points 
      for x,y,w,h in last_points:
         images[count][y:y+h,x:x+w] = 5
   
   
      count = count + 1
      hits = hits + result
   print ("TOTAL: ", len(file_list))
   print ("DIFFS: ", diffs)
   print ("HITS: ", hits)
   fp.close()
   
   
   for file in diffed_files:
      el = file.split("/")
      st = el[-1]
      report_str = st.replace("-stack.jpg", "-report.txt")
      video_str = st.replace("-stack.jpg", ".mp4")
      #cmd = "grep \"Motion Frames:\" `find /mnt/ams2/SD/"  + str(cam_num) + " |grep " + report_str + "`" 
      #output = subprocess.check_output(cmd, shell=True).decode("utf-8")
   
      #output = output.replace("Motion Frames:", "motion_frames=")
      #print (output)
      #exec(output)
      #if len(motion_frames) > 14:
      #   cmd = "find /mnt/ams2/SD/"  + str(cam_num) + " |grep " + video_str 
      #   video_file = subprocess.check_output(cmd, shell=True).decode("utf-8")
      #   print("This is probably a real event?")
      #   print(video_file)
       
sdate = sys.argv[1]
cam_num = sys.argv[2]
  
diff_stills(sdate, cam_num) 

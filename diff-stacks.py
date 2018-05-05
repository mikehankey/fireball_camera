#!/usr/bin/python3

# next steps. save off a cache of the diffs,so we can save time on multiple re-runs. 
# do a crop cnt confirm. 

# script to make master stacks per night and hour from the 1 minute stacks

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure 

from sklearn.cluster import KMeans
from sklearn import datasets

from PIL import Image, ImageChops

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

def stack_stack(pic1, pic2):
   frame_pil = Image.fromarray(pic1)
   stacked_image = pic2
   if stacked_image is None:
      stacked_image = frame_pil 
   else:
      stacked_image=ImageChops.lighter(stacked_image,frame_pil)
   return(stacked_image)



def compute_straight_line(x1,y1,x2,y2,x3,y3):
   print ("COMP STRAIGHT", x1,y1,x2,y2,x3,y3)
   if x2 - x1 != 0:
      a = (y2 - y1) / (x2 - x1)
   else:
      a = 0
   if x3 - x1 != 0:
      b = (y3 - y1) / (x3 - x1)
   else:
      b = 0
   straight_line = a - b
   if (straight_line < 1):
      straight = "Y"
   else:
      straight = "N"
   return(straight_line)


def crop_center(img,cropx,cropy):
    y,x = img.shape
    startx = x//2-(cropx//2) +12
    starty = y//2-(cropy//2) + 4
    return img[starty:starty+cropy,startx:startx+cropx]

def fig2data ( fig ):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw ( )
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = np.fromstring ( fig.canvas.tostring_argb(), dtype=np.uint8 )
    buf.shape = ( w, h,4 )
 
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll ( buf, 3, axis = 2 )
    return buf

def kmeans_cluster(points, num_clusters):
   points = np.array(points) 
   print(points)
   clusters = []
   cluster_points = []
   colors = ('r', 'g', 'b')
   est = KMeans(n_clusters=num_clusters)
   est.fit(points)



   print (est.labels_)
   print (len(points))
   ({i: np.where(est.labels_ == i)[0] for i in range(est.n_clusters)})

   for i in set(est.labels_):
      index = est.labels_ == i
      cluster_idx = np.where(est.labels_ == i)
      for idxg in cluster_idx:
         for idx in idxg:
            idx = int(idx)
            point = points[idx]
            #print ("IDX:",i, idx, point)
            cluster_points.append(point)
      clusters.append(cluster_points)
      cluster_points = []
   #print(points[:,0])
   #print(points[:,1])
   int_lb = est.labels_.astype(float)

   #fig = gcf()

   fig = Figure()
   canvas = FigureCanvas(fig)

   plot = fig.add_subplot(1,1,1)
   plot.scatter(points[:,0], points[:,1], c=[plt.cm.Spectral(float(i) / 10) for i in est.labels_])

   for cluster in clusters:
      cxs = []
      cys = []
      for cp in cluster:
         x,y,w,h = cp
         cxs.append(x)
         cys.append(y)
      if len(cxs) > 3:
         plot.plot(np.unique(cxs), np.poly1d(np.polyfit(cxs, cys, 1))(np.unique(cxs)))

   plt.xlim(0,640)
   plt.ylim(0,480)
   plot.invert_yaxis()
   fig.canvas.draw()
   fig.savefig("/tmp/plot.png", dpi=fig.dpi)
   #plt.show()


   return(clusters)

 

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
   stars = []
   obj_points = []
   big_cnts = []
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


   possible_stars = []
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
            if used_pts[key] == 0 and used_pts[key2] == 0 :
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
      # of all the close points, make sure that at least 2 points < 25 px dist exist.  
      conf_closest = []
      for cls in closest:
         if cls[0] < 100:
            conf_closest.append(cls)
      if len(closest) > 0:
         distsort = np.unique(closest, axis=0)
         dist,angle,x1,y1,x2,y2 = distsort[0]
         if dist < 50 and len(conf_closest) > 1:
            line_segments.append((int(dist),int(angle),int(x1),int(y1),int(x2),int(y2)))
            obj_points.append((int(x1),int(y1), int(w1), int(h1)))
         else: 
            possible_stars.append((int(x1),int(y1),int(w1),int(h1)))
         
         #print("CLOSEST LINE SEGMENT FOR PT: ", distsort[0])
      #else: 
         #print("ERROR! no close points to this one!", x1,y1)
      if w1 > 15 or h1 > 15:
      #   print ("BIG!!! We have a big object here likely containing many line segments.")
         big_cnts.append((int(x1),int(y1),int(w1),int(h1)))

   for star in possible_stars:
      close = 0
      for line in line_segments: 
         dist,angle,x1,y1,x2,y2 = line 
         star_dist = calc_dist(star[0], star[1], x1,y1)
         #print ("STARDIST: ", star_dist, star[0], star[1], x1,y1)
         if star_dist < 60:
            close = 1
 
      if close == 1:
         obj_points.append(star)
      else:
         stars.append(star)

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
         
         
     


   if len(line_group) >= 2:
      line_groups.append(line_group)
   else:
      for line in line_group:
         orphan_lines.append(line)

   # now make sure all of the line segments in the line group can connect to at least one of the other segments
   #print ("Total Line Groups as of now:", len(line_groups))
   #print ("Total Orphan Lines as of now:", len(orphan_lines))

   #print ("Confirm the line segments are all part of the same group", len(line_groups))


   #print ("TOTAL POINTS: ", len(points))
   #print ("TOTAL LINE GROUPS: ", len(line_groups))
   #print ("ORPHAN GROUPS: ", len(orphan_lines))


   #for point in points:
      #print ("POINT: ", point)


   gc = 1
   if len(line_groups) > 0:
      for line_group in line_groups:
         lc = 1
         for line in line_group:
            #print("LINE:", line)
            dist,ang,x1,y1,x2,y2 = line
            #confirm_angle = find_angle(x1,y1,x2,y2)
            #print ("GROUP", gc, lc, line, ang, confirm_angle) 
            lc = lc + 1
         gc = gc + 1
   #else:

   #make sure the obj points are not false positives, if so move to stars.
   (line_groups, orphan_lines, stars, obj_points, big_cnts) = conf_objs(line_groups, orphan_lines, stars, obj_points, big_cnts)

 
   return(line_groups, orphan_lines, stars, obj_points, big_cnts)

def conf_objs(line_groups, orphan_lines, stars, obj_points, big_cnts):
   print ("CONF OBJS")
   print ("LINE GROUPS", len(line_groups))
   print ("OBJ POINTS", len(obj_points))
   conf_line_groups = []

   mx = []
   my = []
   mw = [] 
   mh = []
   #first lets check the line groups and make sure at least 3 points are straight
   for line_group in line_groups:
      mx = []
      my = []
      mw = [] 
      mh = []
      lgc = 0
      for dist,ang,x1,y1,x2,y2 in line_group:
         mx.append(x1)
         my.append(y1)
         print (dist, ang, x1,y1,x2,y2)
         print (lgc, "adding MX", x1, mx)
         print (lgc, "adding MYs", y1, my)
         #mx.append(x2)
         #my.append(y2)
         lgc = lgc + 1
      if len(mx) > 2:
         print ("MXs", mx)
         print ("MYs", my)
         st = compute_straight_line(mx[0],my[0],mx[1],my[1],mx[2],my[2])
      else: 
         st = 100
      if st <= 1:
         print ("This group is straight")    
         conf_line_groups.append(line_group)
      else:
         print ("This group is NOT straight")    
         orphan_lines.append(line_group)

   cc = 0 

   mx = []
   my = []
   mw = [] 
   mh = []

   for x,y,h,w in obj_points:
      mx.append(x)
      my.append(y)
      mw.append(w)
      mh.append(h)
      cc = cc + 1

   if len(mx) > 2:
      st = compute_straight_line(mx[0],my[0],mx[1],my[1],mx[2],my[2])
   else: 
      st = 100 

   if st <= 1: 
      print ("At least 3 of these are straight, we can continue.", st)
   else:
      print ("These 3 objects are not straight, and thus false!", st)
      for x,y,h,w in obj_points:
         stars.append((x,y,h,w))
      obj_points = [] 
   return(line_groups, orphan_lines, stars, obj_points, big_cnts)

def clean_line_groups(line_groups, orphan_lines):

   cleaned_line_groups = []
   cleaned_line_group = []
   for line_group in line_groups:
      if len(line_group) == 2:
         # make sure these two groups are close enough to each other to be grouped. 
         (dist,angle,x1,y1,x2,y2) = line_group[0]
         (xdist,xangle,xx1,xy1,xx2,xy2) = line_group[1]
         group_dist = calc_dist(x1,y1,xx1,xy1)
         if group_dist > 50 or (angle -5 < xangle < angle + 5):
            orphan_lines.append(line_group[0])
            orphan_lines.append(line_group[1])
         else:
            cleaned_line_group.append(line_group[0])
            cleaned_line_group.append(line_group[1])
      else:
            cleaned_line_groups.append(line_group)

   line_groups = cleaned_line_groups
   print("CLG:", line_groups)
   return(cleaned_line_groups, orphan_lines)

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

def find_best_thresh(image, thresh_limit, type):
   go = 1
   while go == 1: 
      _, thresh = cv2.threshold(image, thresh_limit, 255, cv2.THRESH_BINARY)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      if type == 0:
         cap = 4 
      else:
         cap = 100
      if len(cnts) > cap:
         thresh_limit = thresh_limit + 1 
      
      else: 
         bad = 0
         for (i,c) in enumerate(cnts):
            x,y,w,h = cv2.boundingRect(cnts[i])
            if w == image.shape[1]: 
               bad = 1
            #if type == 0 and (w >= 10 or h > 10): 
            #   bad = 1
            #if type == 0 and (w == 1 or h == 1): 
            #   bad = 1
         if bad == 0: 
            go = 0
         else:
            thresh_limit = thresh_limit + 1 
      print ("CNTs, BEST THRESH:", str(len(cnts)), thresh_limit)
   #thresh_limit = thresh_limit + 3
   print ("CNTs, BEST THRESH:", str(len(cnts)), thresh_limit)
   #time.sleep(3)
   return(thresh_limit)


def find_objects2(timage, tag, current_image, filename):
   stars = []
   big_cnts = []
   obj_points = []
   image = timage
   thresh_limit = 10 
   thresh_limit = find_best_thresh(image, thresh_limit, 0)
   # find best thresh limit code here!
   line_objects = []
   points = []
   orphan_lines = []
   _, thresh = cv2.threshold(image, thresh_limit, 255, cv2.THRESH_BINARY)
   (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   #print ("CNTS:", len(cnts))
   hit = 0
   objects = []
   if len(cnts) < 500:
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         if w > 1 and h > 1:
            if (w < 10 and h <10):
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
                     print("adding some points",x,y,w,h)
                     points.append((x,y,w,h))
      

            points.append((x,y,w,h))
            #objects.append((x,y,w,h))
         #else:
            #image[y:y+h,x:x+w] = [0]
   else: 
      print ("WAY TO MANY CNTS:", len(cnts))
      thresh_limit = thresh_limit + 5

   return(points)

   # find line objects
   if (len(objects) + len(points)) > 0:
      line_groups, orphan_lines, stars, obj_points = find_objects(0, points)
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
   if len(orphan_lines) >= 1:
      final_group, reject_group = regroup_lines(reject_group)
      if len(final_group) > 1:
         final_groups.append(final_group)
      if len(final_group) > 0:
         print ("Adopted! : ", final_group)
      orphan_lines = reject_group
   if len(orphan_lines) >= 1:
      final_group, reject_group = regroup_lines(reject_group)
      if len(final_group) > 1:
         final_groups.append(final_group)
      if len(final_group) > 0:
         print ("Adopted! : ", final_group)
      orphan_lines = reject_group

   final_groups, orphan_lines = clean_line_groups(final_groups, orphan_lines)
   clusters= []
   clusters_ab= []
   last_x = None
   last_y = None
   last_ang = None
   ang = None
   if len(points) > 3:
      num_clusters = int(len(points)/3)
      clusters = kmeans_cluster(points, num_clusters)
      #print ("MIKE CLUSTERS", len(clusters))
      for cluster in clusters:
         cxs = []
         cys = []
         for cp in cluster:
            x,y,w,h = cp
            cxs.append(x)
            cys.append(y)
            if last_x is not None:
               ang = find_angle(x,y,last_x,last_y)
               print ("CLUSTER ANGLE:", x,y,last_x,last_y,ang)
               if last_ang is not None:
                  if ang - 5 < last_ang < ang + 5:
                     cv2.line(image, (x,y), (last_x,last_y), (200), 4)    
            last_x = x
            last_y = y 
            last_ang = ang 
         a, b = best_fit (cxs,cys)
         mnx = min(cxs)
         mny = min(cys)
         mmx = max(cxs)
         mmy = max(cys)
         cv2.rectangle(image, (mnx,mny), (mmx, mmy), (255),1)
         #print ("MIKE MIKE XS,", cxs)
         #print ("MIKE MIKE YS,", cys)
         clusters_ab.append((a,b))
         print ("MIKE AB,", a,b)


   print ("FINAL ANALYSIS")
   print (final_groups)
   print ("--------------")
   print ("File Name: ", filename)
   print ("Total Points:", len(points))
   print ("Total Line Segments:", len(line_segments))
   print ("Total Final Line Groups:", len(final_groups))
   print ("Total Clusters:", len(clusters))
   cl =0 
   for a,b in clusters_ab:
      print ("Cluster " + str(cl + 1) + " " + str(len(clusters[cl])) + " points")
      print ("LINE AB " + str(a) + " " + str(b))
      cl = cl + 1
   #print (final_groups)
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
         #print (gc, lc, line)    
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
      #print("ORPHAN:", line)
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


   #for x,y,w,h in points:
   #   if w > 25 or h > 25:
   #      cv2.rectangle(image, (x,y), (x+w+5, y+h+5), (255),1)
   #   else:
   #      cv2.circle(image, (x,y), 20, (120), 1)



   edges = cv2.Canny(image.copy(),thresh_limit,255)
   el = filename.split("/");
   fn = el[-1]
   cv2.putText(current_image, "File Name: " + fn,  (10,440), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   cv2.putText(current_image, str(tag),  (10,450), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   cv2.putText(current_image, "Points: " + str(len(points)),  (10,460), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   cv2.putText(current_image, "Line Groups: " + str(len(final_groups)),  (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
   blend = cv2.addWeighted(image, .2, current_image, .8,0)

   np_plt = cv2.imread("/tmp/plot.png")
   np_plt = cv2.cvtColor(np_plt, cv2.COLOR_BGR2GRAY)
   hh, ww = np_plt.shape
   crop = cv2.resize(np_plt, (0,0), fx=1.1, fy=1.1)
   crop = crop_center(crop, 640,480)

   #blend = cv2.addWeighted(blend, .5, crop, .5,0)
   #for x,y in stars:
   #   cv2.circle(blend, (x,y), 5, (255), 1)




     

   #exit()
   return(line_groups, points, clusters)

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
            #print("FINAL GROUP:", line, angle, s_ang, mean_angle)
            found = 0
            for (dd,aa,ax1,ay1,ax2,ay2) in final_group:
               if ax1 == x1 and ay1 == y1: 
                  found = 1
            if found == 0:
               final_group.append((dist,angle,x1,y1,x2,y2))
 
         else:
            #print("REJECT GROUP:",line, angle, s_ang, mean_angle)
            reject_group.append((dist,angle,x1,y1,x2,y2))

   if len(line_segments ) > 0:
      sdist,sangle,sx1,sy1,sx2,sy2 = line_segments[0]
      for line in line_segments:
         dist,angle,x1,y1,x2,y2 = line
         s_ang = find_angle(sx1,sy1,x1,y1)
         tdist = calc_dist(x1,y1,sx1,sy1)
         if sangle - 10 <= angle <= sangle + 10 and tdist < 20:
            found = 0
            for (dd,aa,ax1,ay1,ax2,ay2) in final_group:
               if ax1 == x1 and ay1 == y1: 
                  found = 1
            if found == 0:
               print("FINAL GROUP:", line, angle, s_ang, mean_angle)
               final_group.append((dist,angle,x1,y1,x2,y2))
         else:
            #print("REJECT GROUP:",line, angle, s_ang, mean_angle)
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
         if i % 5 == 0:
            canvas[0:480,i:i+3] = 0
         if j % 5 == 0:
            canvas[j:j+3,0:640] = 0
   #print ("CROP", crop.shape[0])
   #if crop.shape[0] > 25:
      #cv2.imshow('pepe', canvas)
      #cv2.waitKey(1000)
            


   last_cnts = []
   while go == 1:
     _, thresh = cv2.threshold(canvas, thresh_limit, 255, cv2.THRESH_BINARY)
     (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
     cnt_limit = int((w + h) / 20)
     if cnt_limit < 5:
        cnt_limit = 5
     if cnt_limit > 25:
        cnt_limit = 25 
     #print ("CNTS at thresh:", len(cnts), thresh_limit)
     thresh_limit = thresh_limit - 2
     if len(cnts) >= cnt_limit:
        for (i,c) in enumerate(cnts):
           x,y,w,h = cv2.boundingRect(cnts[i])
           if w > 1 and h > 1:
              cnt_pts.append((x,y,w,h))
     if len(last_cnts) >= len(cnt_pts) and len(last_cnts) > cnt_limit:
        #cnt_pts = last_cnts
        go = 0
     if thresh_limit < 5:
        cnt_pts = last_cnts
        go = 0
     if len(cnts) > 70:
        go = 0
     #print ("CNTS: ", len(cnts))
     #print ("LAST CNTS: ", len(last_cnts))
     #print ("THRESH LIMIT: ", thresh_limit)
     #cv2.imshow('pepe', thresh)
     #cv2.waitKey(100)
     last_cnts = cnt_pts

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

   #before_diff = cv2.absdiff(current_image.astype(current_image.dtype), before_image,)
   #after_diff = cv2.absdiff(current_image.astype(current_image.dtype), after_image,)
   #before_after_diff = cv2.absdiff(before_image.astype(current_image.dtype), after_image,)

   #median_three = np.median(np.array((before_image, after_image, current_image)), axis=0)
   median = np.uint8(median)
   #median_sum = np.sum(median)

   #median_diff = cv2.absdiff(median_three.astype(current_image.dtype), median,)

   blur_med = cv2.GaussianBlur(median, (5, 5), 0)

   # find bright areas in median and mask them out of the current image
   tm = find_best_thresh(blur_med, 30, 1)
   _, median_thresh = cv2.threshold(blur_med, tm, 255, cv2.THRESH_BINARY)
   tm = find_best_thresh(blur_med, 30, 1)
   _, median_thresh = cv2.threshold(blur_med, tm, 255, cv2.THRESH_BINARY)

   (_, cnts, xx) = cv2.findContours(median_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   hit = 0
   real_cnts = []
   #print ("CNTS: ", len(cnts))
   #if len(cnts) < 1000:
      #for (i,c) in enumerate(cnts):
         #x,y,w,h = cv2.boundingRect(cnts[i])
         #if True:
           # w = w + 20
           # h = h + 20
           # #x = x - 20
           # y = y - 20
           # if x < 0:
           #    x = 0
            #if y < 0:
               #y = 0
            #if x+w > current_image.shape[1]:
               #x = current_image.shape[1]-1
#            if y+h > current_image.shape[0]:
#               y = current_image.shape[0]-1
#         if w > 0 and h > 0:
#            mask = current_image[y:y+h, x:x+w]
            #cv2.rectangle(current_image, (x,y), (x+w+5, y+h+5), (255),1)
            #for xx in range(0, mask.shape[1]):
               #for yy in range(0, mask.shape[0]):
               #   mask[yy,xx] = randint(0,6)
#            blur_mask = cv2.GaussianBlur(mask, (5, 5), 0)
            #current_image[y:y+h,x:x+w] = blur_mask
            #median[y:y+h,x:x+w] =blur_mask

   # find the diff between the masked median and the masked current image
   blur_cur = cv2.GaussianBlur(current_image, (5, 5), 0)
   blur_med = cv2.GaussianBlur(median, (5, 5), 0)
   cur_med_diff = cv2.absdiff(blur_cur.astype(blur_cur.dtype), blur_med,)

   blend = cv2.addWeighted(current_image, .5, cur_med_diff, .5,0)

   #cur_med_diff =- median


   return(blend, current_image, filename)

def inspect_image(med_stack_all, background, median, before_image, current_image, after_image, avg_cnt,avg_tot,avg_pts,filename):
   rois = []
   big_cnts = []
   line_groups = []
   orphan_lines = []
   obj_points = []
   stars = []
   image_diff = cv2.absdiff(current_image.astype(current_image.dtype), background,)
   orig_image = current_image
   current_image = image_diff
   blend, current_image, filename = diff_all(None, background, median, before_image, current_image, after_image,filename)

   points = find_objects2(blend, "Current Median Diff Blend",  current_image, filename)
   if len(points) > 2:
      line_groups, orphan_lines, stars, obj_points, big_cnts = find_objects(0, points)
   if len(obj_points) > 2:
      line_groups, orphan_lines, stars2, obj_points, big_cnts = find_objects(0, obj_points)
      stars = stars + stars2

   print ("---FINAL ANALYSIS---")
   print ("File: ", filename)
   print ("Total Points: ", len(points))
   print ("Line Groups: ", len(line_groups))
   lg_points = 0
   lg = 1
   for line in line_groups:
      print ("   Group " + str(lg) + ": " + str(len(line)))
      lg = lg + 1
      lg_points = lg_points + len(line)
   print ("Total Line Group Points: ", lg_points)
   print ("Orphan Lines: ", len(line_groups))
   print ("Stars: ", len(stars))
   print ("Obj Points: ", len(obj_points))
   print ("Big CNTS: ", len(big_cnts))


   for x,y,w,h in big_cnts:
      cv2.rectangle(blend, (x,y), (x+w+5, y+h+5), (255),1)

   #for x,y,w,h in obj_points:
   #   if w > 25 or h > 25:
   #      cv2.rectangle(blend, (x,y), (x+w+5, y+h+5), (255),1)
   #   else:
   #      cv2.circle(blend, (x,y), 20, (120), 1)
   #for x,y,w,h in stars:
   #   if w > 25 or h > 25:
   #      cv2.rectangle(blend, (x,y), (x+w+5, y+h+5), (255),1)
   #   else:
   #      cv2.circle(blend, (x,y), 5, (120), 1)



   return(blend, points, line_groups, stars, obj_points, big_cnts)



def parse_file_date(orig_video_file):
   #print(orig_video_file)
   if ".mp4" in orig_video_file:
      stacked_image_fn = orig_video_file.replace(".mp4", "-stack.jpg") 
      star_image_fn = orig_video_file.replace(".mp4", "-stars.jpg")
      report_fn = orig_video_file.replace(".mp4", "-stack-report.txt")
      video_report = orig_video_file.replace(".mp4", "-report.txt")

      trim_file = orig_video_file.replace(".mp4", "-trim.mp4")

   else:
      stacked_image_fn = orig_video_file.replace(".avi", "-stack.jpg") 
      trim_file = orig_video_file.replace(".avi", "-trim.avi")
      star_image_fn = orig_video_file.replace(".avi", "-stars.jpg")
      report_fn = orig_video_file.replace(".avi", "-stack-report.txt")
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
   return(sun_status, sun_alt)

def find_closest_cnts(sx,sy,cnts): 
   close = 0
   for (i,c) in enumerate(cnts):
      x,y,w,h = cv2.boundingRect(cnts[i])
      dist = calc_dist(sx,sy,x,y)
      if 5 < dist < 30: 
         close = close + 1
   return(close)    

def sort_cnts(cnts, method="left-to-right"):
	# initialize the reverse flag and sort index
	reverse = False
	i = 0
 
	# handle if we need to sort in reverse
	if method == "right-to-left" or method == "bottom-to-top":
		reverse = True
 
	# handle if we are sorting against the y-coordinate rather than
	# the x-coordinate of the bounding box
	if method == "top-to-bottom" or method == "bottom-to-top":
		i = 1
 
	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv2.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))
 
	# return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)
      
def find_noisy_cnts(image):
   #cv2.imshow('pepe', image)
   #cv2.waitKey(1000)
   noise = 0
   (_, noisy_cnts, xx) = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   for (i,c) in enumerate(noisy_cnts):
      #x,y,w,h = cv2.boundingRect(noisy_cnts[i])
      x,y,w,h = cv2.boundingRect(c)
      convex = cv2.isContourConvex(c)  
      peri = cv2.arcLength(c, True)
      approx = cv2.approxPolyDP(c, 0.01 * peri, True)
      #print ("NOISE:", len(noisy_cnts), int(peri), len(approx), convex)

      if w <= 1 and h <= 1:
         noise = noise + 1
         image[y:y+h,x:x+w] = [0]
      if len(approx) > 10 and convex is False  :
         # this is a cloud or a plane, so mute it out. 
         #print ("DELETE!")
         image[y:y+h,x:x+w] = [0]

      if peri > 100 and convex is False :
         # this is a cloud or a plane, so mute it out. 

         ny = y - 10
         nx = x - 10
         if ny < 0: 
            ny = 0
         if nx < 0: 
            nx = 0

         image[ny:y+h+10,nx:x+w+10] = [0]
         noise = noise + 1
         #print ("removing big cnt:", x,y,w,h,convex,peri,len(approx))

   return(noise, image)

def find_cnts(image):
   last_angle = -1000
   angle = 0
   dist = 0
   (_, cnts_by_area, xx) = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   cnts_by_area = sorted(cnts_by_area, key = cv2.contourArea, reverse = True)[:25]
   print ("CNT BY AREA LENGTH: ", len(cnts_by_area))
   # Mute out the big non-convex cnts
   for (i,c) in enumerate(cnts_by_area):
      x,y,w,h = cv2.boundingRect(cnts_by_area[i])
      #cv2.rectangle(image, (x,y), (x+w+5, y+h+5), (255),1)
      #cv2.imshow('pepe', image)
      #cv2.waitKey(1000)
      #print ("Mute: ", w,h)
      peri = cv2.arcLength(c, True)
      approx = cv2.approxPolyDP(c, 0.02 * peri, True)
      convex = cv2.isContourConvex(c)  
      close = find_closest_cnts(x,y,cnts_by_area)
      if peri > 100 and convex == False or (close <= 2):
         # This is a cloud or plane some other non meteor object
         #print ("BAD CNT!!! MUTE IT!", peri, convex)
         ny = y - 10
         nx = x - 10
         if ny < 0: 
            ny = 0
         if nx < 0: 
            nx = 0
         #image[ny:y+h+10,nx:x+w+10] = [0]



   color = 255
   good = 0
   bad = 0
   good_angles = 0
   (_, cnts_by_loc, xx) = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   cnts_by_loc = sorted(cnts_by_loc, key = cv2.contourArea, reverse = True)[:25]
   if len(cnts_by_loc) > 3:
      cnts_by_loc,bb = sort_cnts(cnts_by_loc, method="left-to-right")
   good_points = []
   for (i,c) in enumerate(cnts_by_loc):
      x,y,w,h = cv2.boundingRect(cnts_by_loc[i])
      peri = cv2.arcLength(c, True)
      approx = cv2.approxPolyDP(c, 0.02 * peri, True)
      convex = cv2.isContourConvex(c)  
      # how many cnts are close to this one? 
      close = find_closest_cnts(x,y,cnts_by_loc)
      if peri > 100 and convex == False:
         # This is a cloud or plane some other non meteor object
         #image[y-10:y+h+10,x-10:x+w+10] = [0]
         good = good - 1

      if i > 0:
         last_angle = angle
         angle = find_angle(x,y,last_x,last_y)
         #print ("FIND ANGLE FOR: ", x,y,last_x,last_y, angle, last_angle)
         dist = calc_dist(x,y,last_x,last_y)
      else:
         first_x = x
         first_y = y 

      # if this is the last cnt in the group
      if i == len(cnts_by_loc) - 1:
         last_angle = angle
         angle = find_angle(first_x, first_y, x, y)
         dist = calc_dist(first_x, first_y, x, y)

      # if this angle agrees with the last angle
      if (angle - 10 < last_angle < angle + 10) and (1 < close < 10) and (w > 1 and h > 1):
         good_angles = good_angles + 1
         cv2.circle(image, (x,y), 20, (255), 1)
         good_points.append((x,y,w,h))


      if len(approx) > 0 and peri > 0 and w > 1 and h > 1 and close > 0 and close < 10:
         print ("Peri:", str(i), x,y,w,h, str(int(peri)), str(len(approx)), str(int(angle)), str(int(last_angle)), str(int(dist)), convex, close)
         cv2.putText(image, "PA " + str(i) + " " + str(int(peri)) + " " + str(len(approx)) + " " + str(int(angle)) + " " + str(last_angle) + " " + str(int(dist)) + " " + str(convex) + " " + str(close),  (100,10+(i*15)), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
         cv2.putText(image, str(i),  (x+10,y+10), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
         if len(approx) < 3 :
            color = 50
         elif 3 <= len(approx) < 5:
            color = 155 
         elif 5 <= len(approx) < 15:
            color = 255
         elif len(approx) > 15:
            color = 75
         if peri > 100:
            color = 75

      if peri > 100 and convex == False:
         # This is a cloud or plane some other non meteor object
         #image[y-10:y+h+10,x-10:x+w+10] = [0]
         good = good - 1
      else: 
         good = good + 1
         rect = cv2.minAreaRect(c)
         box = cv2.boxPoints(rect)
         box = np.int0(box)
         image = cv2.drawContours(image, [box], 0,(color),1)

        

         #if len(approx) >= 5:
         #   elp = cv2.fitEllipse(c)
         #   image = cv2.ellipse(image,elp,(0,255,0),2)
 
         #cv2.rectangle(image, (x,y), (x+w+5, y+h+5), (color),1)
      last_x = x
      last_y = y
  
   # ok we should be left with just 'good cnts'
   # lets run some tests on the 'good cnts'
   # test to make sure they can form a line or share a similar angle
   if len(good_points) >= 3:
      line_groups, orphan_lines, stars, obj_points, big_cnts = find_objects(0, good_points)
      print("Line Groups:", len(line_groups))
      print("Orphan Lines:", len(orphan_lines))
      print("Stars:", len(stars))
      print("Obj Points:", len(obj_points))


   return(good, good_angles, image)


def diff_stills(sdate, cam_num, show_video):
   if show_video == 1:
      cv2.namedWindow('pepe')
   image_thresh = []
   med_last_objects = []
   last_objects = deque(maxlen=5) 
   diffed_files = []
   config = read_config("conf/config-1.txt")
   video_dir = "/mnt/ams2/SD/"
   images = []
   images_orig = []
   images_blend = []
   images_info = []
   count = 0
   last_image = None
   last_thresh_sum = 0
   hits = 0
   avg_cnt = 0
   avg_tot = 0
   avg_pts = 0
   count = 0

   glob_dir = video_dir + "proc/" + sdate + "/" + "*cam" + str(cam_num) + "-blend.jpg"
   report_file = video_dir + "proc/" + sdate + "/" + sdate + "-cam" + str(cam_num) + "-report.txt"
   master_stack_file = video_dir + "proc/" + sdate + "/" + sdate + "-cam" + str(cam_num) + "-master_stack.jpg"

   #cv2.namedWindow('pepe')
   mask_file = "conf/mask-" + str(cam_num) + ".txt"
   file_exists = Path(mask_file)
   mask_exists = 0
   still_mask = [0,0,0,0]
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

   for filename in (glob.glob(glob_dir)):
       capture_date = parse_file_date(filename)
       sun_status, sun_alt = day_or_night(config, capture_date)
       #if sun_status != 'day' and int(sun_alt) < -4:
          #print("NIGHTTIME", capture_date, filename, sun_status)
       file_list.append(filename)
       #else: 
       #   print ("This is a daytime or dusk file", filename)
   
   sorted_list = sorted(file_list)
   print ("Loading Images...")
   for filename in sorted_list:
      open_cv_image = cv2.imread(filename,0)
      orig_image = open_cv_image
      open_cv_image[440:480, 0:640] = [0]


      images_orig.append(orig_image)
      images.append(open_cv_image)



   print ("Finished Loading Images.", len(sorted_list))
   if len(sorted_list) == 0:
      print ("Pre-processing of stack blends has not happened yet. Aborting...")
      exit()
   diff_sums = []
   height , width =  open_cv_image.shape
   master_stack = None 
   objects = None
   last_line_groups = []
   last_points = []
   count = 0
   cnts_counts = []
   for filename in sorted_list:
      thresh_file = filename.replace("blend", "diff")
      file_exists = Path(thresh_file)
      if (file_exists.is_file()):
         open_cv_image = cv2.imread(thresh_file,0)
         image_thresh.append(open_cv_image)
         sum = np.sum(open_cv_image)
         diff_sums.append(sum)
         # file already exists, just load it and move forward

      else:
         # file doesn't exist yet so make it and save it. 


         print ("THESH: ", thresh_file)
         hit = 0
         detect = 0
         el = filename.split("/")
         fn = el[-1]
         current_image = images[count]
         current_filename = sorted_list[count]
   
         if count >= 2:
            before_image2 = images[count-2]
            before_image = images[count-1]
            before_filename = sorted_list[count-1]
         else:
            before_image2 = images[count+2]
            before_image = images[count+2]
            before_filename = sorted_list[count+2]
   
         if count >= len(sorted_list)-2:
            after_image2 = images[count-3]
            after_image = images[count-2]
            after_filename = sorted_list[count-2]
         else:
            after_image2 = images[count+2]
            after_image = images[count+1]
            after_filename = sorted_list[count+1]

         if count < 25:
            median = np.median(np.array(images[0:count+25]), axis=0)
         elif len(images) - count < 25:
            median = np.median(np.array(images[count-25:count]), axis=0)
         else:
            median = np.median(np.array(images[count-25:count]), axis=0)

         median = np.uint8(median)

         blur_med = cv2.GaussianBlur(median, (5, 5), 0)

         # find bright areas in median and mask them out of the current image
         tm = find_best_thresh(blur_med, 30, 1)

         md = np.median(blur_med)
         av = np.average(blur_med)
         #tm = md + (av /1)

         #median_thresh = cv2.adaptiveThreshold(blur_med,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,1)
         _, median_thresh = cv2.threshold(blur_med, tm, 255, cv2.THRESH_BINARY)


         (_, median_cnts, xx) = cv2.findContours(median_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         med_diff = cv2.absdiff(current_image.astype(current_image.dtype), median,)
         image_diff = cv2.absdiff(current_image.astype(current_image.dtype), before_image,)
         image_diff2 = cv2.absdiff(current_image.astype(current_image.dtype), before_image2,)
         aft_image_diff = cv2.absdiff(current_image.astype(current_image.dtype), after_image,)
         aft_image_diff2 = cv2.absdiff(current_image.astype(current_image.dtype), after_image2,)
         bef_aft_image_diff = cv2.absdiff(before_image.astype(current_image.dtype), after_image,)
         median_three = np.median((image_diff, image_diff2, aft_image_diff, aft_image_diff2, med_diff, current_image), axis=0)
         median_three = np.uint8(median_three)

         # block out bright parts of the median
         for (i,c) in enumerate(median_cnts):
            x,y,w,h = cv2.boundingRect(median_cnts[i])
            my = y - 30
            mx = x - 30
            mmy = y + 30
            mmx = x + 30
            if mmy >= current_image.shape[0]:
               mmy =current_image.shape[0] 
            if mmx >= current_image.shape[1]:
               mmx =current_image.shape[1] 
            image_diff[my:mmy, mx:mmx] = [0]
            #before_image[my:mmy, mx:mmx] = [0]



   
         md = np.median(current_image)
         av = np.average(current_image)
         print ("working on (md,av): ", filename, md, av)
         #thresh_limit = md + (av /1)
         thresh_limit = 10


         #_, thresh = cv2.threshold(median_three, thresh_limit, 255, cv2.THRESH_BINARY)
         thresh = cv2.adaptiveThreshold(median_three,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,-10)
         this_thresh = thresh.copy()
         cnts = []
         real_cnt = 0
         real_cnt_space = 0
         if count >= 1:
            # zero out the bright areas in the last image diff so they don't show up in this one. 
            (_, cnts, xx) = cv2.findContours(last_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for (i,c) in enumerate(cnts):
               x,y,w,h = cv2.boundingRect(cnts[i])
               this_thresh[y-20:y+h+20, x-20:x+w+20] = [0]
               # before_image[y-20:y+h+20, x-20:x+w+20] = [0]
               if w > 1 and h > 1:
                  real_cnt = real_cnt + 1
                  real_cnt_space = real_cnt_space + (w*h)

         last_thresh = thresh

         sum = np.sum(this_thresh)
         diff_sums.append(sum)
         #noise, this_thresh = find_noisy_cnts(this_thresh)
         #if count > 0:


            #cv2.putText(this_thresh, str(before_filename),  (5,460), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
            #cv2.putText(this_thresh, str(current_filename),  (5,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)

         if show_video == 1:
            cv2.imshow('pepe', cv2.convertScaleAbs(median_three))
            cv2.waitKey(100)
            cv2.imshow('pepe', this_thresh)
            cv2.waitKey(100)
         cv2.imwrite(thresh_file, this_thresh)

         image_thresh.append(this_thresh)
         #if (len(image_thresh) > 1000): 
         #   break
         cnts_counts.append((real_cnt,real_cnt_space))
         count = count + 1

   exit()
   md = np.median(diff_sums)
   mav = np.average(diff_sums)
   count = 0
   dfs_count = 0
   noise = 0
   for img in image_thresh:
      current_image = images[count]
      file = sorted_list[count]
      sum = diff_sums[count]
      #cnt_count,cnt_space = cnts_counts[count]
      print(file)
      #noise, img = find_noisy_cnts(img)

      good, good_angles, img = find_cnts(img)
      print ("CNTs,S,Noise,M,A,G,GA:", good, noise, sum, md, mav, good, good_angles)
      #edges = cv2.Canny(img, 30,255)
      blend = cv2.addWeighted(img, .2, current_image, .8,0)
      #cv2.imshow('pepe', img)
      #if good >= 0 and good_angles >= 0:
      #   dfs_count = dfs_count + 1
      #   while(1):
      #      k = cv2.waitKey(33)
      #      if k == 32:
      #         break
      #      if k == 27:
      #         exit()
      #else:
      #   cv2.waitKey(1)
      count = count + 1
   print ("Total Images:", count)
   print ("Total Diffs:", dfs_count)

       
sdate = sys.argv[1]
cam_num = sys.argv[2]
try:
   show_video = int(sys.argv[3])
except:
   show_video = 0
  
diff_stills(sdate, cam_num, show_video) 

from sklearn.cluster import KMeans
import math
import cv2
import sys
import numpy as np
import glob
from collections import deque
from PIL import Image, ImageChops


def median_mask(median_array, img, count):
#   median_array = [] 
#   if count < 11:
#      for i in range(count + 1, count + 11):
#         median_array.append(images[i])
   #elif count > len(images) - 11:
#      for i in range(count-11, count -1):
#         median_array.append(images[i])
#   else:
#      for i in range(count-5, count + 6):
#         median_array.append(images[i])

   median_image = np.median(np.array(median_array), axis=0)
      
   median = np.uint8(median_image)
   
   tval = find_best_thresh(median, -10)
   tval = tval -5 

   med_thresh = cv2.adaptiveThreshold(median,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,tval)
   #_, med_thresh = cv2.threshold(median, 255, 255, cv2.THRESH_BINARY)

   (_, cnts, xx) = cv2.findContours(med_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   for (i,c) in enumerate(cnts):
      x,y,w,h = cv2.boundingRect(cnts[i])
      img[y-10:y+h+10,x-10:x+w+10] = 0
   return(img)

   
def grid_big_cnt(image,x,y,w,h):
   go = 1

   #canvas = np.zeros([480,640], dtype=crop.dtype)
   #canvas[y:y+h,x:x+w] = crop
   for i in range(x,x+w):
      for j in range(y,y+w):
         if i % 10 == 0:
            image[0:480,i:i+2] = 0
         if j % 10 == 0:
            image[j:j+2,0:640] = 0
   return(image)

def stack_stack(pic1, pic2):
   if len(pic1.shape) == 3:
      pic1 = cv2.cvtColor(pic1, cv2.COLOR_BGR2GRAY)
   frame_pil = Image.fromarray(pic1)
   stacked_image = pic2
   if pic2 is not None:
      np_stacked_image = np.asarray(stacked_image)

   if stacked_image is None:
      stacked_image = frame_pil
   else:
      stacked_image=ImageChops.lighter(stacked_image,frame_pil)
   return(stacked_image)


def cluster_size(cluster):
   np_cluster = np.array(cluster)
   min_x = np.min(np_cluster[:,0])
   min_y = np.min(np_cluster[:,1])
   max_x = np.max(np_cluster[:,0])
   max_y = np.max(np_cluster[:,1])
   width = max_x - min_x
   height = max_y - min_y
   return(width,height,min_x,min_y,max_x,max_y)


def best_fit(X, Y):

    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    #print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b

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


def cluster_center(cluster):
   npc = np.array(cluster)
   cx = np.average(npc[:,0])
   cy = np.average(npc[:,1])
   mx = np.max(npc[:,0])
   my = np.max(npc[:,1])
   mnx = np.min(npc[:,0])
   mny = np.min(npc[:,1])
   return(cx,cy,mx,my,mnx,mny)


def cluster_dist ( clusters):
   cluster_dist = []
   cn = 0
   dst_ot = 0
   unmerged_clusters = []
   merged_clusters = []
   new_clusters = []
   for i in range(0,len(clusters)) :
      merged = 0
      cluster = clusters[i]
      cx,cy,mx,my,mnx,mny = cluster_center(cluster)
      for j in range(i+1,len(clusters)) :
         cluster2 = clusters[j]
         ccx, ccy, mx2,my2,mnx2,mny2 = cluster_center(cluster2)
         dist = calc_dist(cx, cy, ccx,ccy)
         dist_mn_mx = calc_dist(mx, my, mnx2,mny2)
         if dist < 75:
            merged_clusters.append(i)
            merged_clusters.append(j)
            merged = 1
         else:
            dst_ot += 1
         cluster_dist.append ((cx, cy, ccx,ccy, dist))
   for cc in range(0, len(clusters)):
      merge = 0
      for mc in merged_clusters:
         if (cc == mc):
            merge = 1
      if merge == 0 and cc not in merged_clusters:
         unmerged_clusters.append((cc))


   new_clusters = []
   merged = []
   for cid in merged_clusters:
      for x,y in clusters[cid]:
         merged.append((x,y))
   if len(merged) > 0:
      new_clusters.append(merged)

   for cid in unmerged_clusters:
      new_clusters.append(clusters[cid])

   return (clusters, cluster_dist, dst_ot)


def kmeans_cluster2(points, num_clusters):
   points =  sorted(points, key=lambda x: x[1])
   clusters = []
   cluster_points = []
   if num_clusters > len(points):
      num_clusters = len(points) - 1 

   est = KMeans(n_clusters=num_clusters)
   est.fit(points)
   ({i: np.where(est.labels_ == i)[0] for i in range(est.n_clusters)})
   for i in set(est.labels_):
      index = est.labels_ == i
      cluster_idx = np.where(est.labels_ == i)
      for idxg in cluster_idx:
         for idx in idxg:
            idx = int(idx)
            point = points[idx]
            cluster_points.append(point)
      clusters.append(cluster_points)
      cluster_points = []
   # find distance from each cluster to the other. If close group together.

   lcx = None
   lcy = None
   cn = 1

   new_clusters, clust_d, dst_ot = cluster_dist(clusters)
   if dst_ot < num_clusters -1 and num_clusters > 1:
      clusters, clust_d = kmeans_cluster2(points, num_clusters -1)
   if dst_ot > num_clusters and num_clusters > 1:
      clusters, clust_d = kmeans_cluster2(points, num_clusters -1)

   clust_d = sorted(clust_d, key=lambda x: x[1])
   new_clusters, clust_d, dst_ot = cluster_dist(clusters)

   # for each of these clusters, examine the points and remove any orphans
   new_cluster = []
   val_clusters = []
   orphan_points = []

   for cluster in new_clusters:
      for x,y in cluster:
         point_bad = 1
         for x2, y2 in cluster:
            if x != x2 and y != y2:
               dist = calc_dist(x,y,x2,y2)
               if dist < 50:
                  point_bad = 0
                  break
         if point_bad == 0:
            new_cluster.append((x,y))
         else: 
            orphan_points.append((x,y))
      if len(new_cluster) > 2:
         val_clusters.append(new_cluster)
      new_cluster = []

   new_clusters = val_clusters
   return(new_clusters, clust_d)


def find_best_thresh(img, tval): 
   tcnt = 1000
   while tcnt > 100:
      thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,tval)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      tval = tval - 2 
      tcnt = len(cnts)
      #print("TVAL:", tval)
   return(tval)


def examine_still(filename, img, last_cnts, past_clusters):
   obj_file = filename.replace("-stacked.jpg", "-objects.jpg")
   txt_file = filename.replace("-stacked.jpg", "-objects.txt")
   #img = cv2.imread(filename,0)
   orig_img = cv2.imread(filename,0)

   

   av = np.average(orig_img)
   md = np.median(orig_img)
   if av > 50:
      cv2.imwrite(obj_file, orig_img)
      return([], [], 0, "avg pixels are too bright.", orig_img)


   #if len(last_cnts) > 0:
   #   for (i,c) in enumerate(last_cnts):
   #      x,y,w,h = cv2.boundingRect(last_cnts[i])
   #      img[y-5:y+h+5, x-5:x+w+5] = [av-5]

   img[440:480, 0:640] = [av]

   tval = find_best_thresh(img, -10)

   points = []
   real_cnts = 0
   thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,tval)
   (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   big_cnt = 0
   print ("CNTS: ", len(cnts))
   if len(cnts) > 0 and len(cnts) < 100:
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         if w > 10 or h > 10:
            img = grid_big_cnt(img, x, y, w,h)
            big_cnt = 1

   if big_cnt == 1:
      thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,tval)
      (_, cnts, xx) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   for (i,c) in enumerate(cnts):
      x,y,w,h = cv2.boundingRect(cnts[i])

      if w > 2 or h > 2:
         cv2.circle(img, (x,y), 5, (125), 1)
         real_cnts = real_cnts + 1
         points.append((x,y))

   if len(points) > 2:
      num_c = int(len(points) / 3)
      if num_c < 2:
         num_c = 2
      if num_c > 10:
         num_c = 10

      (clusters, cluster_d) = kmeans_cluster2(points, num_c)
   else:
      clusters = []
      cluster_d = []

   nn = 0

   # fit cluster points to line and eval
   cxs = []
   cys = []
   rejected_clusters = 0
   good_clusters = []

   for cluster in clusters:
      tcw,tch,tmin_x,tmin_y,tmax_x,tmax_y = cluster_size(cluster)
      tcx = int((tmin_x + tmax_x) / 2)
      tcy = int((tmin_y + tmax_y) / 2)
      bad_cluster = 0
      for ps_clusters in past_clusters:
         for ps_cluster in ps_clusters:
            pcw,pch,pmin_x,pmin_y,pmax_x,pmax_y = cluster_size(ps_cluster)
            if pmin_x - 5 < tcx < pmax_x + 5 and pmin_y -5 < tcy < pmax_y + 5:
               #print("Reject due to Past Cluster:", ps_cluster)
               bad_cluster = bad_cluster + 1
      if bad_cluster > 3 or len(cluster) < 3:
         rejected_clusters = rejected_clusters + 1
      else:
         good_clusters.append(cluster)
            


   for cluster in good_clusters:
      for cp in cluster:
         x,y = cp
         cxs.append(x)
         cys.append(y)
   if len(cxs) >= 2 and len(cys) >= 2:
      a, b = best_fit (cxs,cys)

   new_clusters = []
   for cluster in good_clusters:
      cx,cy,mx,my,mnx,mny = cluster_center(cluster)
      cv2.rectangle(img,(mnx,mny),(mx,my),(255),2)
      text = str(nn)
      cw = mx - mnx
      ch = my - mny
      if (cw > 2 and ch > 2):
    
         cv2.putText(img, text,  (int(cx),int(cy)), cv2.FONT_HERSHEY_SIMPLEX, .4, (255), 1)
         nn = nn + 1
         new_clusters.append(cluster)
      else:
         print("bad cluster", cluster)




   if len(cnts) > 0:
      noise = int((real_cnts / len(cnts)) * 100)
   else:
      noise = 0


   print ("AVG BR, CLUSTERS, CNTS, Real CNTS, SNR:" + str(int(av)) + " " + str(len(clusters)) + " " + str(len(cnts)) + " " + str(real_cnts) + " " + str(noise) + "%")


   # REJECTION FILTERS HERE
   # need to have:
   # at least 1 valid cluster (a cluster with 3 or more points)
   # at least 3 real cnts
   # less than a total of 1000 cnts 
   # an average brightness < 100
   # a SNR > 20%
   # a % of points that are close to the fitted line of the cluster
   status = 1
   status_desc = ""
   valid_clusters = 0
   for cluster in good_clusters:
      if len(cluster) > 2:
         valid_clusters = valid_clusters + 1

   valid_clusters = len(good_clusters)


   for cluster in good_clusters:
      np_cluster = np.array(cluster)
      min_x = np.min(np_cluster[:,0])
      min_y = np.min(np_cluster[:,1])
      max_x = np.max(np_cluster[:,0])
      max_y = np.max(np_cluster[:,1])
      par = np.polyfit(np_cluster[:,0], np_cluster[:,1], 1, full=True)
      slope = par[0][0]
      intercept = par[0][1]
      x1 = [min(np_cluster[:,0]), max(np_cluster[:,0])]
      y1 = [int(slope*xx + intercept) for xx in x1]

      cw,ch,min_x,min_y,max_x,max_y = cluster_size(cluster)

      print ("Slope, Intercept", slope, intercept)
      print ("Cluster W,H", cw, ch)

      cv2.line(img, (x1[0],y1[0]), (x1[1],y1[1]), (200), 1)


   if len(good_clusters) < 1:
      status = 0
      status_desc = "rejected for no good clusters: " + str(good_clusters)


   if valid_clusters <= 0:
      status = 0
      status_desc = "rejected for having less than 1 valid cluster: " + str(valid_clusters)

   if len(cnts) > 1000:
      status = 0
      status_desc = "rejected for having too much noise"
   if av > 50:
      status = 0
      status_desc = "rejected for having average brightness greater than 50"
   if noise < 10:
      status = 0
      status_desc = "rejected for having SNR below 10%:" + str(noise)
   if real_cnts < 3:
      status = 0
      status_desc = "rejected for having less than 3 points:" + str(real_cnts)





   #cv2.imshow('pepe', img)
   cv2.imwrite(obj_file, img)
   fp = open(txt_file, "w")
   fp.write("cnts=" + str(cnts))
   fp.write("clusters=" + str(clusters))
   fp.write("status_desc=" + str(status_desc))
   fp.write("hit=" + str(status))
   fp.close()
   if status == 1:
      #cv2.waitKey(10)
      return(cnts, clusters, 1, status_desc, orig_img)
      #while(1):
      #   k = cv2.waitKey(33)
      #   if k == 32:
      #      return(cnts, clusters, 1, status_desc, orig_img)
      #      break
      #   if k == 27:
      #      exit()
   else:
      print("REJECTED: ", status_desc)
      #cv2.waitKey(10)
      return(cnts, clusters, 0, status_desc, orig_img)


def get_stacked_files(glob_dir, cam_num):
   file_list = []
  
   for filename in (glob.glob(glob_dir + "*cam" + cam_num + "-stacked.jpg")):
       file_list.append(filename)
   sorted_list = sorted(file_list)
   return(sorted_list)

def preload_images(stack_files):
   images = []
   new_stack_files = []
   for filename in stack_files:
      img = cv2.imread(filename,0)

      av = np.average(img)
      if av < 50:
         images.append(img)
         new_stack_files.append(filename)
      else:
         obj_file = filename.replace("stacked.jpg", "objects.jpg")
         cv2.imwrite(obj_file, img)
   return(new_stack_files, images)      
   

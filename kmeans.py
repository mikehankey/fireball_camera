#!/usr/bin/python3 

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn import datasets


def kmeans_cluster(points, num_clusters):
   clusters = []
   cluster_points = []
   colors = ('r', 'g', 'b')

   est = KMeans(n_clusters=3)
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
            print ("IDX:",i, idx, point)
            cluster_points.append(point)
      clusters.append(cluster_points)
   print(points[:,0])
   print(points[:,1])
   int_lb = est.labels_.astype(float)
   plt.scatter(points[:,0], points[:,1], c=[plt.cm.Spectral(float(i) / 10) for i in est.labels_])
   plt.show()
   #print (len(clusters))
   #print (clusters)
      

points = np.array([[164, 436], [157, 423] , [154, 420], [145, 406], [142, 402], [141, 399], [131, 385], [119, 365], [278, 360], [264, 356], [90, 312], [64, 262], [56, 245], [50, 232], [43, 217], [35, 200], [32, 189], [29, 185], [27, 176], [20, 163], [501, 161], [508, 157], [16, 150], [7, 126], [3, 114], [0, 104]])
kmeans_cluster(points, 3)

from PIL import Image
import cv2
import glob
import sys
import numpy as np
path = sys.argv[1]


# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'H264')
out = cv2.VideoWriter('output.avi',fourcc, 5.6, (640,360))

image_list = []
file_list = []
sorted_list = []
for filename in (glob.glob(path + '/*.jpg')): 
    file_list.append(filename)

sorted_list = sorted(file_list)

for filename in sorted_list:
    print (filename)
    open_cv_image = cv2.imread(filename,0)
    height , width =  open_cv_image.shape
    print (height, width)
    #open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    equ = cv2.equalizeHist(open_cv_image)
    rgb_equ = cv2.cvtColor(equ, cv2.COLOR_GRAY2RGB)

    rgb_equ = cv2.fastNlMeansDenoisingColored(open_cv_image,None,10,10,7,21)
    out.write(rgb_equ)
    #out.write(open_cv_image)

out.release()

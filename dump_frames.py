import cv2

file = "test-cal.avi"
cap = cv2.VideoCapture(file)
count = 0
while True:
   frame_file = file.replace(".avi", "-" + str(count) + ".jpg");
   _ , frame = cap.read()
   if frame is None:
      exit()
   cv2.imwrite("jpgs/" + frame_file, frame)
   count = count + 1


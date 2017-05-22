import sys
from PIL import Image, ImageStat

# Covert image to greyscale, return average pixel brightness.
def brightness_method1( im_file ):
   im = Image.open(im_file).convert('L')
   stat = ImageStat.Stat(im)
   return stat.mean[0]

# Covert image to greyscale, return RMS pixel brightness.
def brightness_method2( im_file ):
   im = Image.open(im_file).convert('L')
   stat = ImageStat.Stat(im)
   return stat.rms[0]
  

# Return results of all methods
def brightness_all_method(im_file):
    print(brightness_method1( im_file ))
    print(brightness_method2( im_file )) 

 
# Used with arguments   
if( len(sys.argv) != 0 ):
   brightness_all_method( sys.argv[1])

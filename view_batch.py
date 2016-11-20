from os import listdir
from os.path import isfile, join

mypath = "/var/www/html/out"

files = [f for f in listdir(mypath) if '.avi' in f and isfile(join(mypath, f))]

print files

#!/usr/bin/python3 

from pathlib import Path
import os
import cgi
import cgitb
import pickle

master_conf_file = "/home/ams/fireball_camera/allsky6-conf.pkl"
conf_fields = ['first_name', 'last_name', 'email', 'obs_name', 'city_name', 'state_name', 'device_lat', 'device_lng', 'device_alt']
conf_labels = ['First Name', 'Last Name', 'Email', 'Observatory Name', 'City Name', 'State Name', 'Latitude', 'Longitude', 'Altitude']


def first_time_setup ():
   master_conf = {}
   c = 0
   print("<FORM METHOD=POST>")
   print("<input type=hidden name=act value=save_conf>")
   for field in conf_fields:
      print (conf_labels[c] + ": <input type=text name=" + field + " value=\"\"> <BR>" )
      c = c + 1
   print("<input type=submit name=submit value=\"Save Config\">")

def save_conf():

   master_conf = {}
   saved_obj = {}
   for field in conf_fields:
      value = form.getvalue(field)
      print (field, value, "<BR>")
      master_conf[field] = value

   print ("<PRE>", master_conf)
   save_obj(master_conf, master_conf_file)

   print ("Try to load")
   try:
      saved_obj = load_obj(master_conf_file)
   except Exception as e:
      print (str(e))
   print ("Loaded", saved_obj)


def load_obj(fname ):
   print ("loading obj", fname )
   try:
      with open(fname, 'rb') as f:
         return pickle.load(f)
   except Exception as e:
      print("Failed to load obj", fname, str(e))
      return 0

def save_obj(obj, fname):
   print ("saving obj", fname, obj)
   try:
      with open(fname, 'wb') as f:
         pickle.dump(obj, f, 0)
   except Exception as e:
      print("Failed to save obj", fname, obj, str(e))
   print ("<HR>")

print ("Content-type: text/html\n\n")
form = cgi.FieldStorage()
act = form.getvalue('act')

file_exists = Path(master_conf_file)
if (file_exists.is_file()):
   print("Master Conf File found.")
   new_install = 0
else:
   print("Master Conf File not found... must be a new install?")
   new_install = 1

if act == None and new_install == 1:
   first_time_setup();
elif act == "save_conf":
   save_conf()


#!/usr/bin/python3
import os
import subprocess
import sys
import ephem
import math
from amscommon import read_config
from amscommon import write_config 
from amscommon import put_device_info 
R = 6378.1

def Decdeg2DMS( Decin ):
   Decin = float(Decin)
   if(Decin<0):
      sign = -1
      dec  = -Decin
   else:
      sign = 1
      dec  = Decin

   d = int( dec )
   dec -= d
   dec *= 100.
   m = int( dec*3./5. )
   dec -= m*5./3.
   s = dec*180./5.

   if(sign == -1):
      out = '-%02d:%02d:%06.3f'%(d,m,s)
   else: out = '+%02d:%02d:%06.3f'%(d,m,s)

   return out
   

def RAdeg2HMS( RAin ):
   RAin = float(RAin)
   if(RAin<0):
      sign = -1
      ra   = -RAin
   else:
      sign = 1
      ra   = RAin

   h = int( ra/15. )
   ra -= h*15.
   m = int( ra*4.)
   ra -= m/4.
   s = ra*240.

   if(sign == -1):
      out = '-%02d:%02d:%06.3f'%(h,m,s)
   else: out = '+%02d:%02d:%06.3f'%(h,m,s)
   
   return out

def find_corner (file, x, y):
   cmd = "/usr/local/astrometry/bin/wcs-xy2rd -w " + file + " -x " + x + " -y " + y 
   output = subprocess.check_output(cmd, shell=True)
   (t, radec) = output.decode("utf-8").split("RA,Dec")
   radec = radec.replace('(', '')
   radec = radec.replace(')', '')
   radec = radec.replace('\n', '')
   radec = radec.replace(' ', '')
   ra, dec = radec.split(",")
   print ("ASTR RA/DEC: ", ra,dec)
   radd = float(ra)
   decdd = float(dec)
   ra= RAdeg2HMS(ra)
   #(h,m,s) = ra.split(":")
   #ra = h + " h " + m + " min"
   dec = Decdeg2DMS(dec)
   return(ra, dec, radd, decdd)

def radec_to_azel(ra,dec,lat,lon,alt, caldate):
   body = ephem.FixedBody()
   print ("BODY: ", ra, dec)
   body._ra = ra
   body._dec = dec
   #body._epoch=ephem.J2000 

   ep_date = ephem.Date(caldate)

   obs = ephem.Observer()
   obs.lat = ephem.degrees(lat)
   obs.lon = ephem.degrees(lon)
   obs.date =ep_date 
   print ("OBS DATE:", obs.date)
   print ("LOCAL DATE:", ephem.localtime(ep_date))
   print ("LAT:", lat)
   print ("LON:", lon)
   print ("LAT:", Decdeg2DMS(lat))
   print ("LON:", Decdeg2DMS(lon))
   print ("CALDATE:", caldate)
   obs.elevation=float(alt)
   body.compute(obs)
   az = str(body.az)
   el = str(body.alt)
   print ("AZ/EL", az, el)
   (d,m,s) = az.split(":")
   dd = float(d) + float(m)/60 + float(s)/(60*60)
   az = dd

   (d,m,s) = el.split(":")
   dd = float(d) + float(m)/60 + float(s)/(60*60)
   el = dd
   #az = ephem.degrees(body.az)
   return(az,el)

def find_point (lat, lon, d, brng):
   print ("Bearing is ", brng)
   lat1 = math.radians(lat) #Current lat point converted to radians
   lon1 = math.radians(lon) #Current long point converted to radians

   lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
         math.cos(lat1)*math.sin(d/R)*math.cos(brng))

   lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
               math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

   lat2 = math.degrees(lat2)
   lon2 = math.degrees(lon2)

   return(lat2, lon2)


config = read_config()

lat = 34.60212862
lon = -112.42502225
alt = 1567
caldate = "2017/10/23 7:08:41"

if 1 == 1:
   

   el = sys.argv[1].split("/")
   caldate = el[-1] 
   file = sys.argv[1]
   #caldate = sys.argv[1]
   y = caldate[0:4]
   m = caldate[4:6]
   d = caldate[6:8]

   #t = caldate[8:14]
   h = caldate[8:10]
   mm = caldate[10:12]
   s = caldate[12:14]
   caldate = y + "/" + m + "/" + d + " " + h + ":" + mm + ":" + s 
   print (caldate)
   cords = ""

   x = str(414)
   y = str(360-254)
   y = str(254)
 
   x = str(639)
   y = str(0)

   
   # start 
   (ra, dec, radd, decdd) = find_corner(file, x, y)
  
   print ("RA/DEC of x,y:", ra,dec)
   caldate = "2017/10/23 12:09:43"
   (az, el) = radec_to_azel(ra,dec,lat,lon,alt, caldate)
   print ("X/Y", x,y)
   print ("RA/DEC",  ra, dec)
   print ("AZ/EL", az,el)
   exit() 

   x = str(392)
   y = str(360-359)

   print("\n")   
   (ra, dec, radd, decdd) = find_corner(file, x, y)
   print ("RA/DEC of x,y:", ra,dec)
   (az, el) = radec_to_azel(ra,dec,lat,lon,alt, caldate)
   print ("X/Y", x,y)
   print ("RA/DEC",  ra, dec)
   print ("AZ/EL", az,el)


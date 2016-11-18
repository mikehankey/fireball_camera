import math
import sys
R = 6378.1


#cam_lat = 39.588747
#cam_lon = -76.584339
#center_heading = 34
#el_start = 10
#fov_hdeg = 70
#fov_vdeg = 60

# usage
# python cams.py cam_lat, cam_lon, center_heading, el_start, fov_hdeg, fov_vdeg
# python cams.py 39.588747 -76.584339 34 10 70 60

def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
      #print key, value
    return(config)



def find_point (lat, lon, d, brng):
   lat1 = math.radians(lat) #Current lat point converted to radians
   lon1 = math.radians(lon) #Current long point converted to radians

   lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
         math.cos(lat1)*math.sin(d/R)*math.cos(brng))

   lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
               math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

   lat2 = math.degrees(lat2)
   lon2 = math.degrees(lon2)

   return(lat2, lon2)



def get_fov(cam_lat, cam_lon, center_heading, cam_alt, cam_hdeg, cam_vdeg):

    left_az = float(center_heading) - (float(cam_hdeg) / 2)
    if left_az < 0:
        left_az = left_az + 360
    right_az = float(center_heading) + (float(cam_hdeg) / 2)
    bottom_el = float(cam_alt) - (float(cam_vdeg) / 2)
    bottom_el = float(cam_alt) + (float(cam_vdeg) / 2)
    ra = math.radians(10)
    dist_lb = 80/math.tan(ra)
    ra = math.radians(60)
    dist_lt = 80/math.tan(ra)

    cam_lat = float(cam_lat)
    cam_lon = float(cam_lon)


    (llc_lat, llc_lon) = find_point(cam_lat, cam_lon, dist_lb, math.radians(left_az))
    (ulc_lat, ulc_lon) = find_point(cam_lat, cam_lon, dist_lt, math.radians(left_az))
    (lrc_lat, lrc_lon) = find_point(cam_lat, cam_lon, dist_lb, math.radians(right_az))
    (urc_lat, urc_lon) = find_point(cam_lat, cam_lon, dist_lt, math.radians(right_az))

    cords = str(ulc_lon)+","+str(ulc_lat)+",80000\n" + str(urc_lon)+","+str(urc_lat)+",80000\n" + str(lrc_lon)+","+str(lrc_lat)+",80000\n" + str(llc_lon)+","+str(llc_lat)+",80000\n" + str(ulc_lon)+","+str(ulc_lat)+",80000\n"

    print("<Placemark>\n")
    print("<Polygon>\n")
    print("<extrude>0</extrude>\n")
    print("<altitudeMode>relativeToGround</altitudeMode>\n")
    print("<outerBoundaryIs>\n")
    print("<LinearRing>\n")
    print("<coordinates>\n")
    print (cords)
    print("</coordinates>\n")
    print("</LinearRing>\n")
    print("</outerBoundaryIs>\n")
    print("</Polygon>\n")
    print("</Placemark>\n")

    out = open("fov.txt", "w")
    out.write(cords)
    out.close

#    print ("ULC:", ulc_lat, ulc_lon)
#    print ("URC:", urc_lat, urc_lon)
#    print ("LLC:", llc_lat, llc_lon)
#    print ("LRC:", lrc_lat, lrc_lon)

#(x, cam_lat, cam_lon, center_heading, el_start, cam_hdeg, cam_vdeg) = sys.argv
config = read_config()
get_fov(config['cam_lat'], config['cam_lon'], config['cam_heading'], config['cam_alt'], config['cam_fov_x'], config['cam_fov_y'])


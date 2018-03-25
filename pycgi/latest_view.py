#!/usr/bin/python3
import subprocess 
import time
video_dir = "/mnt/ams2/"
print ("Content-type: text/html\n\n")
css = """
<style>
div {
    width: 512;
    height: 384;
    padding: 5; /* Change this till it fits the dimensions of your video */
    position: relative;
    float: left
}

crapdiv crapiframe {
    width: 100%;
    height: 100%;
    position: absolute;
    display: block;
    top: 0;
    left: 0;
}
</style>
"""
print (css)
rand = time.time()
out = ""
print("<h2>Latest View</h2>")
for cam_num in range(1,7):
   out = out + "<div><img src=\"/out/latest" + str(cam_num) + ".jpg?" + str(rand) + "\" width=512 height=384></div>\n"

print (out)

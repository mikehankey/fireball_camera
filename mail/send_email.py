import sys
from send_email_functions import send_email  

# WARNING ONLY WORK WITH ONE RECEIPIENT
sendEmail([sys.argv[1]],sys.argv[2],sys.argv[3],'Your AMSCam <noreply@castlecomm.com>')
import sys
import smtplib
 
gmail_user = 'noreply@castlecomm.com'  
gmail_password = '1ancel011ancel01'

sent_from = 'Your AMSCam <noreply@castlecomm.com>'

to       = [sys.argv[1]]
subject  = sys.argv[2]
body     = sys.argv[3]
 
email_text = """From: %s  
To: %s
MIME-Version: 1.0
Content-type: text/html  
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try: 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()
    print "Message sent"
except:
    print "Error - impossible to send the recovery email"
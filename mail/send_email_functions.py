import sys
import smtplib
 
# to: array of @
def sendEmail(to,subject,message,sent_from='Your AMSCam <amsmeteors@gmail.com>'): 

    email_text = """From: %s  
To: %s
MIME-Version: 1.0
Content-type: text/html  
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, message) 
 
    try: 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('amsmeteors@gmail.com', '$p@c31$c00l!')
        server.sendmail(sent_from, to, email_text)
        server.close()
        print ("Message sent")
    except:
        print ("Error - impossible to send the recovery email")

#!/usr/bin/python3
import sys
import smtplib
 
# to: array of @
def send_email(to,subject,message,sent_from='Your AMSCam <noreply@castlecomm.com>'): 

    email_text = """From: %s  
    To: %s
    MIME-Version: 1.0
    Content-type: text/html  
    Subject: %s
    
    %s
    """ % (sent_from, ", ".join(to), subject, message)

    gmail_user = 'noreply@castlecomm.com'  
    gmail_password = '1ancel011ancel01'
 
    try: 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print ("Message sent")
    except:
        print ("Error - impossible to send the recovery email")
# -*- coding: utf-8 -*-
    

def htmlmail(mailmsg, isok=False):
        FROMADDR = "guoliangyong@localhost"
        LOGIN    = FROMADDR
        PASSWORD = ""
        TOADDRS  = ["myersguo@gmail.com"]
        SUBJECT  = u"[OK] UI自动化测试--"+ datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
        if isok == False:
                TOADDRS  = ["myersguo@gmail.com"]
                SUBJECT  = u"[FAIL] UI自动化测试--"+ datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

     
    #msg = MIMEMultipart('alternative')
        msg = MIMEText(mailmsg, 'html')
        msg['Subject'] = SUBJECT
        msg['From'] = FROMADDR
        msg['To'] =  ','.join(TOADDRS)
    
        server = smtplib.SMTP('localhost')
        server.set_debuglevel(1)
        server.ehlo()
        server.sendmail(FROMADDR, TOADDRS, msg.as_string())
        server.quit()
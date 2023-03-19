import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



# ------------------------------------------------------------------------
# function: 
#   send_email_smtp(data)
# ------------------------------------------------------------------------
def send_email_smtp(data, email_sender, email_to):
    html_body = "<html>                 \
                    <head></head>       \
                    <body>              \
                        <p>         "   \
                        + data["body"]+ \
                    "   </p>            \
                    </body>             \
                </html>"
    smtp_user = email_sender
    smtp_password = 'nwbozkcunjzuphsc'
    server = 'smtp.gmail.com'
    port = 587
    message = MIMEMultipart()
    message['Subject'] = data["subject"]
    message['From'] = smtp_user
    message['To'] = ", ".join(email_to)


    html_part = MIMEText(html_body, 'html')
    message.attach(html_part)

    s = smtplib.SMTP(server, port)
    s.ehlo()
    s.starttls()
    s.login(smtp_user, smtp_password)
    s.sendmail(smtp_user, email_to, message.as_string())
    s.quit()


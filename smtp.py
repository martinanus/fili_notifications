import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



# ------------------------------------------------------------------------
# function:
#   send_email_smtp()
# ------------------------------------------------------------------------
def send_email_smtp(data, smtp_sender, smtp_password):
    html_body = "<html>                 \
                    <head></head>       \
                    <body>              \
                        <p>         "   \
                        + data["body"]+ \
                    "   </p>            \
                    </body>             \
                </html>"
    server = 'smtp.gmail.com'
    port = 587
    message = MIMEMultipart()
    message['Subject'] = data["subject"]
    message['From']     = smtp_sender
    message['To']       = ", ".join(data["email_to"])


    html_part = MIMEText(html_body, 'html')
    message.attach(html_part)

    s = smtplib.SMTP(server, port)
    s.ehlo()
    s.starttls()
    s.login(smtp_sender, smtp_password)
    s.sendmail(smtp_sender, data["email_to"], message.as_string())
    s.quit()


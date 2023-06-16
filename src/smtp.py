import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



# ------------------------------------------------------------------------
# function:
#   send_email_smtp()
# ------------------------------------------------------------------------
def send_email_smtp(data, smtp_sender, smtp_password):

    email_to = validate_smtp_mail_address(data["email_to"])
    if not email_to:
        print("There is no valid email address to send mail")
        return

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
    message['To']       = ", ".join(email_to)


    html_part = MIMEText(html_body, 'html')
    message.attach(html_part)

    s = smtplib.SMTP(server, port)
    s.ehlo()
    s.starttls()
    s.login(smtp_sender, smtp_password)
    s.sendmail(smtp_sender, email_to, message.as_string())
    s.quit()


def validate_smtp_mail_address(mail_address_l):
    for mail_address in mail_address_l:
        str_len = len(mail_address)
        if str_len < 2:
            mail_address_l.remove(mail_address)
        else:
            if (mail_address.count('@') != 1) or mail_address[0] == '@' or mail_address[str_len-1] == '@':
                mail_address_l.remove(mail_address)
    return mail_address_l
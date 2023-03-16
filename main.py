import functions_framework
import requests

import re
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import json


def get_client():    
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client_bq = bigquery.Client(credentials=credentials, project=credentials.project_id,)

    return client_bq;


def get_configuration():
    query = """
    SELECT *
    FROM `"""+ notif_table_id+ """`"""

    query_job       = client.query(query)  # Make an API request.
    result          = query_job.result()
    df              = result.to_dataframe();
    df              = df.sort_values(by='timestamp', ascending=True)

    return df


def get_notification_msgs():
    
    f       = open(notif_msg_path)
    data    = json.load(f)

    return data


def get_days_as_list(column):
    vals            = df_config[column].values[-1]
    if (vals is None) or (vals[0:7] is 'Ninguna'):
        return []
    vals_trim       = re.sub("[^0-9,-]", "", vals)
    str_l           = re.split(',|-', vals_trim)
    str_l_no_empty  = [i for i in str_l if i]

    return str_l_no_empty


def get_mails_as_list():
    vals            = df_config["internal_email"].values[-1]
    if (vals is None) or ('@' not in vals) or ('.' not in vals):
        return []        
    str_l           = vals.split(',')
    str_l_no_empty  = [i for i in str_l if i]
    
    return str_l_no_empty


def get_invoices_to_notify(relation, days_to_pay):
    
    query = """
    SELECT counterpart, amount, invoice_id, due_date, contact_email, days_to_pay
    FROM `""" + invoice_table_id + """`
    WHERE relation='"""+ relation + """' AND days_to_pay in (""" + ', '.join(days_to_pay) + ')';
    
    query_job       = client.query(query)  
    result          = query_job.result()
    df              = result.to_dataframe();
    
    return df;


def get_pending_invoices():
    
    query = """
    SELECT relation, counterpart, amount, invoice_id, due_date, contact_email, days_to_pay, notification_status
    FROM `""" + invoice_table_id + """`
    WHERE status!='aprobada'""";

    query_job       = client.query(query)  
    result          = query_job.result()
    df              = result.to_dataframe();
    
    return df;


def trigger_receipt_notif():
    internal_pre_notif_days      = get_days_as_list("internal_pre_notif_collect")
    internal_post_notif_days     = get_days_as_list("internal_post_notif_collect")
    internal_post_notif_days     = ['-'+day for day in internal_post_notif_days]
    internal_notif_days         = internal_pre_notif_days + internal_post_notif_days
    
    df = df_inv[(df_inv.relation=='Proveedor') & (df_inv.days_to_pay.isin(internal_notif_days))]
    
    return df.size 


def trigger_payement_notif():
    internal_pre_notif_days      = get_days_as_list("internal_pre_notif_pay")
    internal_post_notif_days     = get_days_as_list("internal_post_notif_pay")
    internal_post_notif_days     = ['-'+day for day in internal_post_notif_days]
    
    internal_notif_days         = internal_pre_notif_days + internal_post_notif_days
    
    df = df_inv[(df_inv.relation=='Cliente') & (df_inv.days_to_pay.isin(internal_notif_days))]
    
    return df.size 


def format_html_table(table):
    table = table.replace('counterpart', 'Cliente')
    table = table.replace('amount', 'Monto ($)')
    table = table.replace('invoice_id', 'ID factura')        
    table = table.replace('due_date', 'Fecha de vencimiento')
    table = table.replace('contact_email', 'E-mail')

    return table


def build_internal_receipt_notif_to_expire():
    body = '';
    receipts_msgs       = notif_msgs["receipts_msgs"]
    internal_pre_notif     = get_days_as_list("internal_pre_notif_collect")
            
    df                  = df_inv[(df_inv.relation=='Cliente') & 
                            ( (df_inv.days_to_pay.isin(internal_pre_notif) | 
                            ( (df_inv.notification_status=='notified') & (df_inv.days_to_pay >= 0)))) ]

    df                  = df.sort_values(by='days_to_pay', ascending=True)                  

    invoice_exp_today_l = df[df.days_to_pay == 0].reset_index();
    if invoice_exp_today_l.size:
        html_table      =  invoice_exp_today_l.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email'], justify='center')
        html_table      = format_html_table(html_table)
        body            += receipts_msgs["invoice_today_msg"]
        body            += html_table
        body            += receipts_msgs["hint_invoice_today_msg"]
    else: 
        body            += receipts_msgs["no_invoice_today_msg"]
    
    if '0' in internal_pre_notif: internal_pre_notif.remove('0')
    
    if internal_pre_notif:
        invoice_pre_exp_l   = df[df.days_to_pay != 0].reset_index();
        if invoice_pre_exp_l.size:
            html_table      =  invoice_pre_exp_l.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email'], justify='center')
            html_table      = format_html_table(html_table)
            body            += receipts_msgs["invoice_to_expire_msg"]
            body            += html_table
            body            += receipts_msgs["hint_invoice_to_expire_msg"]
        else: 
            body            += receipts_msgs["no_invoice_to_expire_msg"]

    return body

def build_internal_receipt_notif_expired():
    body = ''
    internal_post_notif     = get_days_as_list("internal_post_notif_collect")
    internal_post_notif     = ['-'+day for day in internal_post_notif]
    receipts_msgs           = notif_msgs["payements_msgs"]
    
    df                  = df_inv[(df_inv.relation=='Cliente') & 
                            ( (df_inv.days_to_pay.isin(internal_post_notif) | 
                            ( (df_inv.notification_status=='notified') & (df_inv.days_to_pay < 0)))) ]                      
    
    invoice_expired_l   = df.sort_values(by='days_to_pay', ascending=True).reset_index()

    if invoice_expired_l.size:
        html_table      =  invoice_expired_l.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email'], justify='center')
        html_table      = format_html_table(html_table)
        body            += receipts_msgs["invoice_expired_msg"]
        body            += html_table
        body            += receipts_msgs["hint_invoice_expired_msg"]
    else: 
        body            += receipts_msgs["no_invoice_expired_msg"]

    return body

def build_internal_receipt_notif():
    mail_data  = {}

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_internal_receipt_notif_to_expire();
    mail_body += build_internal_receipt_notif_expired();
    mail_body += notif_msgs["ending_msg"]
    
    mail_data["body"]    = mail_body
    mail_data["to"]      = internal_email_notif
    mail_data["subject"] = notif_msgs["receipts_msgs"]["subject"]

    return mail_data


def build_internal_payements_notif_to_expire():
    body                    = ''
    internal_pre_notif      = get_days_as_list("internal_pre_notif_pay")
    paymements_msgs         = notif_msgs["payements_msgs"]
    
    df                  = df_inv[(df_inv.relation=='Proveedor') & 
                            ( (df_inv.days_to_pay.isin(internal_pre_notif) | 
                            ( (df_inv.notification_status=='notified') & (df_inv.days_to_pay >= 0)))) ]

    df                  = df.sort_values(by='days_to_pay', ascending=True)
                        

    invoice_exp_today_l = df[df.days_to_pay == 0].reset_index();
    if invoice_exp_today_l.size:
        html_table      =  invoice_exp_today_l.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email'], justify='center')
        html_table      = format_html_table(html_table)
        body            += paymements_msgs["invoice_today_msg"]
        body            += html_table
        body            += paymements_msgs["hint_invoice_today_msg"]
    else: 
        body            += paymements_msgs["no_invoice_today_msg"]

    if '0' in internal_pre_notif: internal_pre_notif.remove('0')

    invoice_pre_exp_l   = df[df.days_to_pay != 0].reset_index();
    if invoice_pre_exp_l.size:
        html_table      =  invoice_pre_exp_l.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email'], justify='center')
        html_table      = format_html_table(html_table)
        body            += paymements_msgs["invoice_to_expire_msg"]
        body            += html_table
        body            += paymements_msgs["hint_invoice_to_expire_msg"]
    else: 
        body            += paymements_msgs["no_invoice_to_expire_msg"]

    return body

def build_internal_payements_notif_expired():
    body = ''

    internal_post_notif     = get_days_as_list("internal_post_notif_pay")
    internal_post_notif     = ['-'+day for day in internal_post_notif]
    paymements_msgs         = notif_msgs["payements_msgs"]
    
    df                  = df_inv[(df_inv.relation=='Proveedor') & 
                            ( (df_inv.days_to_pay.isin(internal_post_notif) | 
                            ( (df_inv.notification_status=='notified') & (df_inv.days_to_pay < 0)))) ]
    
    invoice_expired_l   = df.sort_values(by='days_to_pay', ascending=True).reset_index()
                
    if invoice_expired_l.size:
        html_table      =  invoice_expired_l.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email'], justify='center')
        html_table      = format_html_table(html_table)
        body            += paymements_msgs["invoice_expired_msg"]
        body            += html_table
        body            += paymements_msgs["hint_invoice_expired_msg"]
    else: 
        body            += paymements_msgs["no_invoice_expired_msg"]

    return body


def build_internal_payements_notif():
    mail_data = {};

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_internal_payements_notif_to_expire();
    mail_body += build_internal_payements_notif_expired();
    mail_body += notif_msgs["ending_msg"]
    
    
    mail_data["body"]    = mail_body
    mail_data["to"]      = internal_email_notif
    mail_data["subject"] = notif_msgs["payements_msgs"]["subject"]

    return mail_data


def send_email_smtp(data):
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
    message['To'] = ", ".join(data["to"])


    html_part = MIMEText(html_body, 'html')
    message.attach(html_part)

    s = smtplib.SMTP(server, port)
    s.ehlo()
    s.starttls()
    s.login(smtp_user, smtp_password)
    s.sendmail(smtp_user, data["to"], message.as_string())
    s.quit()


key_path                = "credentials.json"
notif_msg_path          = "notif_msg.json"
invoice_table_id        = "fili-377220.fili_demo.fili_schedule"
notif_table_id          = "fili-377220.fili_demo.bq_notification_config"
email_sender            = "anusmartin1@gmail.com"
client                  = get_client();
df_config               = get_configuration();
df_inv                  = get_pending_invoices();
notif_msgs              = get_notification_msgs();
internal_email_notif    = get_mails_as_list()   



@functions_framework.http
def main(request):    


    if (trigger_receipt_notif()):
        internal_receipt_mail = build_internal_receipt_notif();
        print(internal_receipt_mail["body"], '\n\n\n')        
        send_email_smtp(internal_receipt_mail)
        print("Receipt notification triggered")
    else:
        print("Receipt notification not triggered")

    
    
    if (trigger_payement_notif()):
        internal_payements_mail  = build_internal_payements_notif()
        print(internal_payements_mail["body"], '\n\n\n')
        send_email_smtp(internal_payements_mail)
        print("Payement notification triggered")
    else:
        print("Payement notification not triggered")

    #external_pre_notif      = get_days_as_list("external_pre_notif")
    #external_post_notif     = get_days_as_list("external_post_notif")
    #print("external_pre_notif:", external_pre_notif)
    #print("external_post_notif: " ,cexternal_post_notif)

    # trigger on mondays (don't forget dues on weekend)
    # Change status to notified in BQ

    return "Las notificaciones fueron enviadas!"

if __name__ == "__main__":
    main('')
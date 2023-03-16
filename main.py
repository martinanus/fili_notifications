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


def get_client():    
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client_bq = bigquery.Client(credentials=credentials, project=credentials.project_id,)
    print("client_bq",client_bq)
    return client_bq;


def get_configuration():
    query = """
    SELECT *
    FROM `fili-377220.fili_demo.bq_notification_config`"""

    print("client, pre query",client)
    query_job       = client.query(query)  # Make an API request.
    result          = query_job.result()
    df              = result.to_dataframe();
    df              = df.sort_values(by='Timestamp', ascending=True)

    return df


def get_days_as_list(column):
    vals            = df_conf[column].values[-1]
    if (vals is None) or (vals[0:7] is 'Ninguna'):
        return []
    vals_trim       = re.sub("[^0-9,-]", "", vals)
    str_l           = re.split(',|-', vals_trim)
    str_l_no_empty  = [i for i in str_l if i]

    return str_l_no_empty


def get_mails_as_list(column):
    vals            = df_conf[column].values[-1]
    if (vals is None) or ('@' not in vals) or ('.' not in vals):
        return []        
    str_l           = vals.split(',')
    str_l_no_empty  = [i for i in str_l if i]
    
    return str_l_no_empty


def get_internal_mails_to_notufy():
    mails            = df_conf["internal_email_notif"].values[-1]
        
    return mails


def get_invoices_to_notify(relation, days_to_pay):
    
    query = """
    SELECT counterpart, amount, invoice_id, contact_email, days_to_pay
    FROM `fili-377220.fili_demo.fili_schedule`
    WHERE relation='"""+ relation + """' AND days_to_pay in (""" + ', '.join(days_to_pay) + ')';
    
    query_job       = client.query(query)  
    result          = query_job.result()
    df              = result.to_dataframe();
    
    return df;


def build_internal_receipt_notif_to_expire():
    body = '';
    internal_pre_notif      = get_days_as_list("internal_pre_notif")
    if internal_pre_notif:            
        df                  = get_invoices_to_notify('Cliente', internal_pre_notif)
        df                  = df.sort_values(by='days_to_pay', ascending=True)
                      
        if '0' in internal_pre_notif: 
            invoice_exp_today_l = df[df.days_to_pay == 0].reset_index();
            if invoice_exp_today_l.size:
                html_table      =  invoice_exp_today_l.to_html(columns=['counterpart', 'contact_email', 'invoice_id', 'days_to_pay', 'amount'], justify='center')
                body           += "<br> Las facturas A COBRAR que vencen hoy son: <br>"
                body           += html_table;
            else:
                body           += "<br> No hay facturar A COBRAR que vencen hoy <br>";
            internal_pre_notif.remove('0')
    
        if internal_pre_notif:
            invoice_pre_exp_l   = df[df.days_to_pay != 0].reset_index();
            if invoice_pre_exp_l.size:
                html_table      =  invoice_pre_exp_l.to_html(columns=['counterpart', 'contact_email', 'invoice_id', 'days_to_pay', 'amount'], justify='center')
                body       += "<br> Las facturas A COBRAR proximas a vencer son: <br>"
                body       += html_table;
            else:
                body       += "<br> No hay facturas A COBRAR proximas a vencer <br>"

    return body

def build_internal_receipt_notif_expired():
    body = ''
    internal_post_notif     = get_days_as_list("internal_post_notif")
    internal_post_notif     = ['-'+day for day in internal_post_notif]
    
    if internal_post_notif:    
        df = get_invoices_to_notify('Cliente', internal_post_notif)        
        invoice_expired_l   = df.sort_values(by='days_to_pay', ascending=True)
        
        if invoice_expired_l.size:
            html_table      =  invoice_expired_l.to_html(columns=['counterpart', 'contact_email', 'invoice_id', 'days_to_pay', 'amount'], justify='center')
            body            += "<br> Las facturas A COBRAR vencidas son: <br>"
            body            += html_table;
        else:
            body            += "<br> No hay facturas A COBRAR vencidas <br>"

    return body

def build_internal_receipt_notif():
    mail_body  = build_internal_receipt_notif_to_expire();
    mail_body += build_internal_receipt_notif_expired();
    
    mail_body = mail_body.replace('counterpart', 'Cliente')
    mail_body = mail_body.replace('contact_email', 'Email')
    mail_body = mail_body.replace('invoice_id', 'ID factura')
    mail_body = mail_body.replace('days_to_pay', 'Dias al vencimiento')
    mail_body = mail_body.replace('amount', 'Monto')

    return mail_body


def build_internal_payements_notif_to_expire():
    body = '';
    internal_pre_notif      = get_days_as_list("internal_pre_notif")
    if internal_pre_notif:            
        df                  = get_invoices_to_notify('Proveedor', internal_pre_notif)
        df                  = df.sort_values(by='days_to_pay', ascending=True)
                        
        if '0' in internal_pre_notif: 
            invoice_exp_today_l = df[df.days_to_pay == 0].reset_index();
            if invoice_exp_today_l.size:
                html_table      =  invoice_exp_today_l.to_html(columns=['counterpart', 'contact_email', 'invoice_id', 'days_to_pay', 'amount'], justify='center')
                body           += "<br>Las facturas A PAGAR que vencen hoy son: <br>"
                body           += html_table;
            else: 
                body           += "<br>No hay facturas A PAGAR que vencen hoy <br>"
            internal_pre_notif.remove('0');
    
        if internal_pre_notif: 
            invoice_pre_exp_l   = df[df.days_to_pay != 0].reset_index();
            if invoice_pre_exp_l.size:
                html_table      =  invoice_pre_exp_l.to_html(columns=['counterpart', 'contact_email', 'invoice_id', 'days_to_pay', 'amount'], justify='center')
                body       += "<br>Las facturas A PAGAR proximas a vencer son: <br>"
                body       += html_table;
            else:
                body       += "<br>No hay facturas A PAGAR proximas a vencer<br>"

    return body

def build_internal_payements_notif_expired():
    body = ''
    internal_post_notif     = get_days_as_list("internal_post_notif")
    internal_post_notif     = ['-'+day for day in internal_post_notif]
    
    if internal_post_notif:    
        df = get_invoices_to_notify('Proveedor', internal_post_notif)
        invoice_expired_l   = df.sort_values(by='days_to_pay', ascending=True)
                
        if invoice_expired_l.size:
            html_table      =  invoice_expired_l.to_html(columns=['counterpart', 'contact_email', 'invoice_id', 'days_to_pay', 'amount'], justify='center')
            body        += "<br>Las facturas A PAGAR vencidas son: <br>"
            body        += html_table;
        else:
            body        += "<br>No hay facturas A PAGAR vencidas<br>"

    return body

def build_internal_payements_notif():
    mail_body  = build_internal_payements_notif_to_expire();
    mail_body += build_internal_payements_notif_expired();
    
    mail_body = mail_body.replace('counterpart', 'Cliente')
    mail_body = mail_body.replace('contact_email', 'Email')
    mail_body = mail_body.replace('invoice_id', 'ID factura')
    mail_body = mail_body.replace('days_to_pay', 'Dias al vencimiento')
    mail_body = mail_body.replace('amount', 'Monto')

    return mail_body


def send_email_smtp(subject, recipient, body):
    html_body = "<html>                 \
                    <head></head>       \
                    <body>              \
                        <p>         "   \
                            + body +    \
                    "   </p>            \
                    </body>             \
                </html>"
    smtp_user = "anusmartin1@gmail.com"
    smtp_password = 'nwbozkcunjzuphsc'
    server = 'smtp.gmail.com'
    port = 587
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = smtp_user
    message['To'] = recipient

    html_part = MIMEText(html_body, 'html')
    message.attach(html_part)

    s = smtplib.SMTP(server, port)
    s.ehlo()
    s.starttls()
    s.login(smtp_user, smtp_password)
    s.sendmail(smtp_user, recipient, message.as_string())
    s.quit()

key_path = "credentials.json"
client = get_client();
df_conf = get_configuration();


@functions_framework.http
def main(request):

    internal_email_notif    = get_internal_mails_to_notufy()     

    internal_receipt_notif = build_internal_receipt_notif();   
    send_email_smtp("Receipts notification", internal_email_notif, internal_receipt_notif)

    internal_payements_notif  = build_internal_payements_notif()    
    send_email_smtp("Payements notification", internal_email_notif, internal_payements_notif)

    return "Las notificaciones internas fueron enviadas!"
import utils
import numpy as np

# ------------------------------------------------------------------------
# function:
#   builf_external_notif()
# ------------------------------------------------------------------------
def build_external_notif(notif_msgs, df_config, df_inv, client, inv_notified_ext, company_name):
    mail_data  = {}

    external_notif_days         = utils.get_external_notification_days(df_config)
    df_client                   = utils.get_inv_to_notify_by_client(df_inv, client, external_notif_days)
    max_day_pre_notif_config    = utils.get_max_day_pre_notif_config(df_config)
    tone                        = get_tone(df_client)
    toned_msgs                  = get_toned_msgs(tone, max_day_pre_notif_config, notif_msgs, company_name, client, df_client)

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_external_notif_expired(toned_msgs, df_client, inv_notified_ext)
    mail_body += build_external_notif_to_expire(toned_msgs, df_client, inv_notified_ext)
    mail_body += build_payment_link(notif_msgs, df_config)
    mail_body += notif_msgs["ending_msg"]

    mail_data["body"]       = mail_body
    mail_data["subject"]    = toned_msgs["subject"]
    mail_data["email_to"]   = utils.get_contact_mail_as_list(df_client)

    return mail_data


# ------------------------------------------------------------------------
# function:
#   build_external_notif_expired()
# ------------------------------------------------------------------------
def build_external_notif_expired(toned_msgs, df_client, inv_notified_ext):
    body = ''

    df_due      = utils.get_due_invoices(df_client)

    if df_due.size:
        html_table      =  utils.get_df_as_external_html_table(df_due)
        html_table      =  utils.format_html_table(html_table, ext_expired=True)
        body            += toned_msgs["greating"]
        body            += toned_msgs["reminder"]
        body            += toned_msgs["expired_msg"]
        body            += html_table
        body            += "<BR>"
        body            += toned_msgs["expired_instr"]

        [inv_notified_ext.append(id) for id in df_due.invoice_id.values]

    return body

# ------------------------------------------------------------------------
# function:
#   build_external_notif_to_expire()
# ------------------------------------------------------------------------
def build_external_notif_to_expire(toned_msgs, df_client, inv_notified_ext):
    body = ''

    df_pre_exp  = utils.get_pre_exp_invoices(df_client)

    if df_pre_exp.size:
        html_table      =  utils.get_df_as_external_html_table(df_pre_exp)
        html_table      =  utils.format_html_table(html_table)
        body            += toned_msgs["to_expire"]
        body            += html_table
        body            += "<BR>"

        [inv_notified_ext.append(id) for id in df_pre_exp.invoice_id.values]

    return body


# ------------------------------------------------------------------------
# function:
#   build_payment_link()
# ------------------------------------------------------------------------
def build_payment_link(notif_msgs, df_config):
    body = ''

    gateway_interest  = df_config.gateway_interest[0]

    if gateway_interest:
        payment_link = df_config.payment_link[0]
        body            += notif_msgs["payment_link_msg"].format(payment_link=payment_link)
        body            += notif_msgs["payment_confirmation_msg"]

    return body


# ------------------------------------------------------------------------
# function:
#   get_toned_msgs()
# ------------------------------------------------------------------------
def get_toned_msgs(tone, max_day_pre_notif_config, notif_msgs, company_name, client, df_client):

    total_debt                  = utils.get_total_debt(df_client)
    due_amount                  = utils.get_due_debt(df_client)
    to_expire_amount            = utils.get_to_expire_debt(df_client)
    oldest_invoice_id           = utils.get_oldest_invoice_id(df_client)
    oldest_invoice_date         = utils.get_oldest_invoice_date(df_client)

    if tone is 0:
        tone_msgs       = notif_msgs["pre_exp_msgs"]

        subject         = tone_msgs["subject"].format(company_name=company_name,to_expire_amount=to_expire_amount, max_day_pre_notif_config=max_day_pre_notif_config)
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format(company_name=company_name)
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 1:
        tone_msgs = notif_msgs["expired_1_msgs"]

        subject         = tone_msgs["subject"].format(company_name=company_name,due_amount=due_amount)
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format(total_debt=total_debt,due_amount=due_amount)
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 2:
        tone_msgs = notif_msgs["expired_2_msgs"]

        subject         = tone_msgs["subject"].format(company_name=company_name,due_amount=due_amount)
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format(oldest_invoice_id=oldest_invoice_id,oldest_invoice_date=oldest_invoice_date)
        expired_msg     = tone_msgs["invoice_expired_msg"].format(due_amount=due_amount)
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 3:
        tone_msgs = notif_msgs["expired_3_msgs"]

        subject         = tone_msgs["subject"].format(company_name=company_name,due_amount=due_amount)
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format(due_amount=due_amount)
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 4:
        tone_msgs = notif_msgs["expired_4_msgs"]

        subject         = tone_msgs["subject"].format(due_amount=due_amount)
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"]
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"].format(due_amount=due_amount)
        to_expire       = tone_msgs["invoice_to_expire_msg"]


    toned_dict = {  "subject"       : subject,
                    "greating"      : greating,
                    "reminder"      : reminder,
                    "expired_msg"   : expired_msg,
                    "expired_instr" : expired_instr,
                    "to_expire"     : to_expire}


    return toned_dict



# ------------------------------------------------------------------------
# function:
#   get_tone()
# ------------------------------------------------------------------------
def get_tone(df_client):

    tone_by_days_range  = get_tone_by_days_range(df_client)
    max_tone_allowed    = get_max_tone_allowed( df_client)

    if tone_by_days_range > max_tone_allowed :
        tone = max_tone_allowed
    else:
        tone = tone_by_days_range

    return tone

# ------------------------------------------------------------------------
# function:
#   get_tone_by_days_range()
# ------------------------------------------------------------------------
def get_tone_by_days_range(df_client):
    days_to_pay = df_client.days_to_pay.values
    max_day = np.sort(days_to_pay)[0]

    if max_day < -80:
        tone = 4
    elif max_day in range(-80, -50):
        tone = 3
    elif max_day in range(-50, -20):
        tone = 2
    elif max_day in range(-20, 0):
        tone = 1
    else:
        tone = 0

    return tone


# ------------------------------------------------------------------------
# function:
#   get_max_tone_allowed()
# ------------------------------------------------------------------------
def get_max_tone_allowed(df_client):
    notif_status_arr = df_client.notification_status_ext.unique()
    max_notif = np.sort(notif_status_arr)[-1]

    if max_notif in ["notified_3", "notified_4"]:
        tone = 4
    elif max_notif in ["notified_2"]:
        tone = 3
    elif max_notif in ["notified_1"]:
        tone = 2
    else:
        tone = 1

    return tone


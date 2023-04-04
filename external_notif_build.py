import utils

# ------------------------------------------------------------------------
# function:
#   builf_external_notif()
# ------------------------------------------------------------------------
def build_external_notif(notif_msgs, df_config, df_inv, client, inv_notified_ext, company_name):
    mail_data  = {}

    max_day_pre_notif_config    = utils.get_max_day_pre_notif_config(df_config)
    toned_msgs                  = get_toned_msgs(notif_msgs, company_name, client, df_inv, max_day_pre_notif_config)

    mail_body  = notif_msgs["starting_msg"]

    external_notif_days     = utils.get_external_notification_days(df_config)
    df_client               = utils.get_inv_to_notify_by_client(df_inv, client, external_notif_days)

    mail_body += build_external_notif_expired(toned_msgs, df_client, inv_notified_ext)
    mail_body += build_external_notif_to_expire(toned_msgs, df_client, inv_notified_ext)

    mail_body += build_payment_link(notif_msgs, df_config)

    mail_body += notif_msgs["ending_msg"].format(company_name)

    mail_data["body"]       = mail_body
    mail_data["subject"]    = toned_msgs["subject"]
    mail_data["email_to"]   = utils.get_contact_mails_as_list(df_client)

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
        body            += notif_msgs["payment_link_msg"].format(payment_link)
        body            += notif_msgs["payment_confirmation_msg"].format("MAIL TO NOTIFY")

    return body

# ------------------------------------------------------------------------
# function:
#   get_toned_msgs()
# ------------------------------------------------------------------------
def get_toned_msgs(external_msgs, company_name, client, df_inv, max_day_pre_notif_config):
    tone = 1 #TODO - Get tone

    total_debt                  = utils.get_total_debt(client, df_inv)
    due_amount                  = utils.get_due_debt(client, df_inv)
    due_amount                  = utils.get_due_debt(client, df_inv)
    to_expire_amount            = utils.get_to_expire_debt(client, df_inv)
    oldest_invoice_id           = utils.get_oldest_invoice_id(client, df_inv)
    oldest_invoice_date         = utils.get_oldest_invoice_date(client, df_inv)

    if tone is 0:
        tone_msgs       = external_msgs["pre_exp_msgs"]

        subject         = tone_msgs["subject"].format(company_name,to_expire_amount, max_day_pre_notif_config)
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format(company_name)
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 1:
        tone_msgs = external_msgs["expired_1_msgs"]

        subject         = tone_msgs["subject"].format(company_name,due_amount)
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format(total_debt,"due_amount")
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 2:
        tone_msgs = external_msgs["expired_2_msgs"]

        subject         = tone_msgs["subject"].format(company_name,"due_amount")
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format(oldest_invoice_id,oldest_invoice_date)
        expired_msg     = tone_msgs["invoice_expired_msg"].format("due_amount")
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 3:
        tone_msgs = external_msgs["expired_3_msgs"]

        subject         = tone_msgs["subject"].format(company_name,"due_amount")
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"].format("due_amount")
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"]
        to_expire       = tone_msgs["invoice_to_expire_msg"]
    elif tone is 4:
        tone_msgs = external_msgs["expired_4_msgs"]

        subject         = tone_msgs["subject"].format("due_amount")
        greating        = tone_msgs["greating"]
        reminder        = tone_msgs["reminder"]
        expired_msg     = tone_msgs["invoice_expired_msg"]
        expired_instr   = tone_msgs["invoice_expired_instruction"].format("due_amount")
        to_expire       = tone_msgs["invoice_to_expire_msg"]


    toned_dict = {  "subject"       : subject,
                    "greating"      : greating,
                    "reminder"      : reminder,
                    "expired_msg"   : expired_msg,
                    "expired_instr" : expired_instr,
                    "to_expire"     : to_expire}


    return toned_dict

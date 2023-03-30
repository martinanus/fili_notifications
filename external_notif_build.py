import utils

# ------------------------------------------------------------------------
# function:
#   builf_external_notif()
# ------------------------------------------------------------------------
def build_external_notif(notif_msgs, df_config, df_inv, client, inv_notified_ext):
    mail_data  = {}
    external_msgs       = notif_msgs["pre_exp_msgs"]

    mail_body  = notif_msgs["starting_msg"]


    external_notif_days     = utils.get_external_notification_days(df_config)
    df_client               = utils.get_inv_to_notify_by_client(df_inv, client, external_notif_days)

    mail_body += build_external_notif_expired(external_msgs, df_client, inv_notified_ext)
    mail_body += build_external_notif_to_expire(external_msgs, df_client, inv_notified_ext)

    mail_body += build_payment_link(notif_msgs, df_config)

    mail_body += notif_msgs["ending_msg"]

    mail_data["body"]    = mail_body
    mail_data["subject"] = external_msgs["subject"]

    return mail_data


# ------------------------------------------------------------------------
# function:
#   build_external_notif_expired()
# ------------------------------------------------------------------------
def build_external_notif_expired(external_msgs, df_client, inv_notified_ext):
    body = ''

    df_due      = utils.get_due_invoices(df_client)

    if df_due.size:
        html_table      =  utils.get_df_as_html_table(df_due)
        html_table      =  utils.format_html_table(html_table)
        body            += external_msgs["invoice_expired_msg"]
        body            += html_table

        [inv_notified_ext.append(id) for id in df_due.invoice_id.values]

    return body

# ------------------------------------------------------------------------
# function:
#   build_external_notif_to_expire()
# ------------------------------------------------------------------------
def build_external_notif_to_expire(external_msgs, df_client, inv_notified_ext):
    body = ''

    df_pre_exp  = utils.get_pre_exp_invoices(df_client)

    if df_pre_exp.size:
        html_table      =  utils.get_df_as_html_table(df_pre_exp)
        html_table      =  utils.format_html_table(html_table)
        body            += external_msgs["invoice_to_expire_msg"]
        body            += html_table

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
        body            += notif_msgs["payment_link_msg"]
        body            += '<a href="'+ payment_link +'">'+ payment_link +'</a> <BR><BR>'
        body            += notif_msgs["payment_confirmation_msg"]

    return body

import utils

# ------------------------------------------------------------------------
# function:
#   build_internal_receipt_notif()
# ------------------------------------------------------------------------
def build_internal_receipt_notif(notif_msgs, df_config, df_inv, inv_notified_int, looker_link):
    mail_data  = {}
    receipts_msgs       = notif_msgs["receipts_msgs"]

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_internal_receipt_notif_expired(receipts_msgs, df_inv, inv_notified_int, looker_link)
    mail_body += build_internal_receipt_notif_to_expire(receipts_msgs, df_config, df_inv, inv_notified_int, looker_link)
    mail_body += notif_msgs["ending_msg"]

    mail_data["body"]       = mail_body
    mail_data["subject"]    = receipts_msgs["subject"]
    mail_data["email_to"]   = utils.get_internal_mails_as_list(df_config)

    return mail_data


# ------------------------------------------------------------------------
# function:
#   build_daily_due_notif()
# ------------------------------------------------------------------------
def build_daily_due_notif(notif_msgs, df_config, df_inv, df_crm, inv_notified_int, looker_link):
    mail_data  = {}
    daily_due_msgs       = notif_msgs["daily_due_msgs"]

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_daily_due_payment_notif(daily_due_msgs, df_inv, df_crm, inv_notified_int)
    mail_body += build_daily_due_receipt_notif(daily_due_msgs, df_inv, df_crm, inv_notified_int)
    mail_body += daily_due_msgs["looker_referal_msg"].format(looker_link=looker_link)
    mail_body += notif_msgs["ending_msg"]

    mail_data["body"]       = mail_body
    mail_data["subject"]    = daily_due_msgs["subject"]
    mail_data["email_to"]   = utils.get_internal_mails_as_list(df_config)

    return mail_data


# ------------------------------------------------------------------------
# function:
#   build_daily_due_payment_notif()
# ------------------------------------------------------------------------
def build_daily_due_payment_notif(daily_due_msgs, df_inv, df_crm, inv_notified_int):
    body = ''

    df_out              = utils.get_df_outcome(df_inv)
    df_today_due_inv    = utils.get_today_due_invoices(df_out)
    df_payment_data     = utils.merge_crm_data(df_today_due_inv, df_crm)

    if not df_payment_data.empty:
        html_table      =  utils.get_df_as_daily_due_payment_html_table(df_payment_data)
        html_table      =  utils.format_html_table(html_table)
        body            += daily_due_msgs["invoice_payment_msg"]
        body            += html_table
        body            += daily_due_msgs["hint_invoice_payment_msg"]
        [inv_notified_int.append(id) for id in df_payment_data.invoice_unique_key.values]

    return body


# ------------------------------------------------------------------------
# function:
#   build_daily_due_receipt_notif()
# ------------------------------------------------------------------------
def build_daily_due_receipt_notif(daily_due_msgs, df_inv, df_crm, inv_notified_int):
    body = ''

    df_in               = utils.get_df_income(df_inv)
    df_today_due_inv    = utils.get_today_due_invoices(df_in)
    df_payment_data     = utils.merge_crm_data(df_today_due_inv, df_crm)

    if not df_payment_data.empty:
        html_table      =  utils.get_df_as_daily_due_receipt_html_table(df_payment_data)
        html_table      =  utils.format_html_table(html_table)
        body            += daily_due_msgs["invoice_receipt_msg"]
        body            += html_table
        body            += daily_due_msgs["hint_invoice_receipt_msg"]
        [inv_notified_int.append(id) for id in df_payment_data.invoice_unique_key.values]

    return body


# ------------------------------------------------------------------------
# function:
#   build_internal_receipt_notif_expired()
# ------------------------------------------------------------------------
def build_internal_receipt_notif_expired(receipts_msgs, df_inv, inv_notified_int, looker_link):
    body = ''

    df_inc      = utils.get_df_income(df_inv)
    df_due_inc  = utils.get_due_invoices(df_inc)

    if not df_due_inc.empty:
        html_table      =  utils.get_df_as_internal_html_table(df_due_inc)
        html_table      =  utils.format_html_table(html_table)
        body            += receipts_msgs["invoice_expired_msg"]
        body            += html_table
        body            += receipts_msgs["hint_invoice_expired_msg"].format(looker_link=looker_link)
        [inv_notified_int.append(id) for id in df_due_inc.invoice_unique_key.values]
    else:
        body            += receipts_msgs["no_invoice_expired_msg"]

    return body

# ------------------------------------------------------------------------
# function:
#   build_internal_receipt_notif_to_expire()
# ------------------------------------------------------------------------
def build_internal_receipt_notif_to_expire(receipts_msgs, df_config, df_inv, inv_notified_int, looker_link):
    body = ''

    limit_days       = utils.get_periodicity_in_days(df_config)
    if (limit_days < 0):
        return body

    df_inc           = utils.get_df_income(df_inv)
    df_upcoming_inc  = utils.get_upcoming_invoices(df_inc, limit_days)


    if not df_upcoming_inc.empty:
        html_table      =  utils.get_df_as_internal_html_table(df_upcoming_inc)
        html_table      =  utils.format_html_table(html_table)
        body            += receipts_msgs["invoice_to_expire_msg"].format(highest_notif_day=limit_days)
        body            += html_table
        body            += receipts_msgs["hint_invoice_to_expire_msg"].format(looker_link=looker_link)
        [inv_notified_int.append(id) for id in df_upcoming_inc.invoice_unique_key.values]
    else:
        body            += receipts_msgs["no_invoice_to_expire_msg"].format(highest_notif_day=limit_days)

    return body



# ------------------------------------------------------------------------
# function:
#   build_internal_payements_notif()
# ------------------------------------------------------------------------
def build_internal_payements_notif(notif_msgs, df_config, df_inv, inv_notified_int, looker_link):
    mail_data = {}
    paymements_msgs         = notif_msgs["payements_msgs"]

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_internal_payements_notif_expired(paymements_msgs, df_inv, inv_notified_int, looker_link)
    mail_body += build_internal_payements_notif_to_expire(paymements_msgs, df_config, df_inv, inv_notified_int)
    mail_body += notif_msgs["ending_msg"]


    mail_data["body"]       = mail_body
    mail_data["subject"]    = paymements_msgs["subject"]
    mail_data["email_to"]   = utils.get_internal_mails_as_list(df_config)

    return mail_data


# ------------------------------------------------------------------------
# function:
#   build_internal_payements_notif_expired()
# ------------------------------------------------------------------------
def build_internal_payements_notif_expired(paymements_msgs, df_inv, inv_notified_int, looker_link):
    body = ''

    df_out      = utils.get_df_outcome(df_inv)
    df_due_out  = utils.get_due_invoices(df_out)


    if not df_due_out.empty:
        html_table      =  utils.get_df_as_internal_html_table(df_due_out)
        html_table      =  utils.format_html_table(html_table)
        body            += paymements_msgs["invoice_expired_msg"]
        body            += html_table
        body            += paymements_msgs["hint_invoice_expired_msg"].format(looker_link=looker_link)
        [inv_notified_int.append(id) for id in df_due_out.invoice_unique_key.values]
    else:
        body            += paymements_msgs["no_invoice_expired_msg"]

    return body


# ------------------------------------------------------------------------
# function:
#   build_internal_payements_notif_to_expire()
# ------------------------------------------------------------------------
def build_internal_payements_notif_to_expire(paymements_msgs, df_config, df_inv, inv_notified_int):
    body = ''

    limit_days       = utils.get_periodicity_in_days(df_config)
    if (limit_days < 0):
        return body

    df_out           = utils.get_df_outcome(df_inv)
    df_upcoming_out  = utils.get_upcoming_invoices(df_out, limit_days)


    if not df_upcoming_out.empty:
        html_table      =  utils.get_df_as_internal_html_table(df_upcoming_out)
        html_table      =  utils.format_html_table(html_table)
        body            += paymements_msgs["invoice_to_expire_msg"].format(highest_notif_day=limit_days)
        body            += html_table
        body            += paymements_msgs["hint_invoice_to_expire_msg"]
        [inv_notified_int.append(id) for id in df_upcoming_out.invoice_unique_key.values]
    else:
        body            += paymements_msgs["no_invoice_to_expire_msg"].format(highest_notif_day=limit_days)


    return body
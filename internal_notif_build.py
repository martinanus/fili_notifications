import utils

# ------------------------------------------------------------------------
# function:
#   build_internal_receipt_notif()
# ------------------------------------------------------------------------
def build_internal_receipt_notif(notif_msgs, df_config, df_inv, inv_notified, looker_config_link):
    mail_data  = {}
    receipts_msgs       = notif_msgs["receipts_msgs"]

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_internal_receipt_notif_to_expire(receipts_msgs, df_config, df_inv, inv_notified)
    mail_body += build_internal_receipt_notif_expired(receipts_msgs, df_config, df_inv, inv_notified, looker_config_link)
    mail_body += notif_msgs["ending_msg"]

    mail_data["body"]    = mail_body
    mail_data["subject"] = receipts_msgs["subject"]

    return mail_data

# ------------------------------------------------------------------------
# function:
#   build_internal_receipt_notif_to_expire()
# ------------------------------------------------------------------------
def build_internal_receipt_notif_to_expire(receipts_msgs, df_config, df_inv, inv_notified):
    body = ''

    internal_pre_notif_days  = utils.get_days_as_list(df_config, "internal_pre_notif_collect")

    df = get_inv_relation_days_prepost (df_inv, 'Cliente', internal_pre_notif_days, is_pre=True)

    invoice_exp_today_df = df[df.days_to_pay == 0].reset_index()
    if invoice_exp_today_df.size:
        html_table      =  utils.get_df_as_html_table(invoice_exp_today_df)
        html_table      =  utils.format_html_table(html_table)
        body            += receipts_msgs["invoice_today_msg"]
        body            += html_table
        body            += receipts_msgs["hint_invoice_today_msg"]
        [inv_notified.append(id) for id in invoice_exp_today_df.invoice_id.values]
    else:
        body            += receipts_msgs["no_invoice_today_msg"]

    if '0' in internal_pre_notif_days: internal_pre_notif_days.remove('0')

    highest_notif_day = utils.get_highest_value_in_list(internal_pre_notif_days)

    invoice_pre_exp_df   = df[df.days_to_pay != 0].reset_index()
    if invoice_pre_exp_df.size:
        html_table      =  utils.get_df_as_html_table(invoice_pre_exp_df)
        html_table      =  utils.format_html_table(html_table)
        body            += receipts_msgs["invoice_to_expire_msg_1"]
        body            += highest_notif_day
        body            += receipts_msgs["invoice_to_expire_msg_2"]
        body            += html_table
        body            += receipts_msgs["hint_invoice_to_expire_msg"]
        [inv_notified.append(id) for id in invoice_pre_exp_df.invoice_id.values]
    else:
        body            += receipts_msgs["no_invoice_to_expire_msg_1"]
        body            += highest_notif_day
        body            += receipts_msgs["no_invoice_to_expire_msg_2"]

    return body

# ------------------------------------------------------------------------
# function:
#   build_internal_receipt_notif_expired()
# ------------------------------------------------------------------------
def build_internal_receipt_notif_expired(receipts_msgs, df_config, df_inv, inv_notified, looker_config_link):
    body = ''
    internal_post_notif_days     = utils.get_days_as_list(df_config, "internal_post_notif_collect", neg_list=True)

    invoice_expired_df = get_inv_relation_days_prepost (df_inv, 'Cliente', internal_post_notif_days, is_pre=False)

    if invoice_expired_df.size:
        html_table      =  utils.get_df_as_html_table(invoice_expired_df)
        html_table      =  utils.format_html_table(html_table)
        body            += receipts_msgs["invoice_expired_msg"]
        body            += html_table
        body            += receipts_msgs["hint_invoice_expired_msg_1"]
        body            += '<a href="'+ looker_config_link +'">'+ receipts_msgs["hint_invoice_expired_msg_2"] +'</a>'
        body            += receipts_msgs["hint_invoice_expired_msg_3"]
        [inv_notified.append(id) for id in invoice_expired_df.invoice_id.values]
    else:
        body            += receipts_msgs["no_invoice_expired_msg"]

    return body

# ------------------------------------------------------------------------
# function:
#   build_internal_payements_notif()
# ------------------------------------------------------------------------
def build_internal_payements_notif(notif_msgs, df_config, df_inv, inv_notified):
    mail_data = {}
    paymements_msgs         = notif_msgs["payements_msgs"]

    mail_body  = notif_msgs["starting_msg"]
    mail_body += build_internal_payements_notif_to_expire(paymements_msgs, df_config, df_inv, inv_notified)
    mail_body += build_internal_payements_notif_expired(paymements_msgs, df_config, df_inv, inv_notified)
    mail_body += notif_msgs["ending_msg"]


    mail_data["body"]    = mail_body
    mail_data["subject"] = paymements_msgs["subject"]

    return mail_data

# ------------------------------------------------------------------------
# function:
#   build_internal_payements_notif_to_expire()
# ------------------------------------------------------------------------
def build_internal_payements_notif_to_expire(paymements_msgs, df_config, df_inv, inv_notified):
    body                    = ''
    internal_pre_notif_days      = utils.get_days_as_list(df_config, "internal_pre_notif_pay")

    df = get_inv_relation_days_prepost (df_inv, 'Proveedor', internal_pre_notif_days, is_pre=True)

    invoice_exp_today_df = df[df.days_to_pay == 0].reset_index()
    if invoice_exp_today_df.size:
        html_table      =  utils.get_df_as_html_table(invoice_exp_today_df)
        html_table      =  utils.format_html_table(html_table)
        body            += paymements_msgs["invoice_today_msg"]
        body            += html_table
        body            += paymements_msgs["hint_invoice_today_msg"]
        [inv_notified.append(id) for id in invoice_exp_today_df.invoice_id.values]
    else:
        body            += paymements_msgs["no_invoice_today_msg"]

    if '0' in internal_pre_notif_days: internal_pre_notif_days.remove('0')

    highest_notif_day = utils.get_highest_value_in_list(internal_pre_notif_days)

    invoice_pre_exp_df   = df[df.days_to_pay != 0].reset_index()
    if invoice_pre_exp_df.size:
        html_table      =  utils.get_df_as_html_table(invoice_pre_exp_df)
        html_table      =  utils.format_html_table(html_table)
        body            += paymements_msgs["invoice_to_expire_msg_1"]
        body            += highest_notif_day
        body            += paymements_msgs["invoice_to_expire_msg_2"]
        body            += html_table
        body            += paymements_msgs["hint_invoice_to_expire_msg"]
        [inv_notified.append(id) for id in invoice_pre_exp_df.invoice_id.values]
    else:
        body            += paymements_msgs["no_invoice_to_expire_msg_1"]
        body            += highest_notif_day
        body            += paymements_msgs["no_invoice_to_expire_msg_2"]


    return body

# ------------------------------------------------------------------------
# function:
#   build_internal_payements_notif_expired()
# ------------------------------------------------------------------------
def build_internal_payements_notif_expired(paymements_msgs, df_config, df_inv, inv_notified):
    body = ''

    internal_post_notif_days     = utils.get_days_as_list(df_config, "internal_post_notif_pay", neg_list=True)

    invoice_expired_df = get_inv_relation_days_prepost (df_inv, 'Proveedor', internal_post_notif_days, is_pre=False)

    if invoice_expired_df.size:
        html_table      =  utils.get_df_as_html_table(invoice_expired_df)
        html_table      =  utils.format_html_table(html_table)
        body            += paymements_msgs["invoice_expired_msg"]
        body            += html_table
        body            += paymements_msgs["hint_invoice_expired_msg"]
        [inv_notified.append(id) for id in invoice_expired_df.invoice_id.values]
    else:
        body            += paymements_msgs["no_invoice_expired_msg"]

    return body


# ------------------------------------------------------------------------
# function:
#   get_inv_relation_days_prepost()
# ------------------------------------------------------------------------
def get_inv_relation_days_prepost (df_inv, relation, days, is_pre):
    if is_pre:
        df                  = df_inv[(df_inv.relation==relation) &
                                ( (df_inv.days_to_pay.isin(days) |
                                ( (df_inv.notification_status_int=='notified') & (df_inv.days_to_pay >= 0)))) ]
    else:
        df                  = df_inv[(df_inv.relation==relation) &
                                ( (df_inv.days_to_pay.isin(days) |
                                ( (df_inv.notification_status_int=='notified') & (df_inv.days_to_pay < 0)))) ]
    df                  = df.sort_values(by='days_to_pay', ascending=True).reset_index()

    return df
import utils

# ------------------------------------------------------------------------
# function:
#   builf_external_notif()
# ------------------------------------------------------------------------
def build_external_notif(notif_msgs, df_config, df_inv, client, inv_notified_ext, company_name, fili_web_url):
    mail_data  = {}

    df_inc                = utils.get_df_income(df_inv)
    df_client             = utils.get_inv_by_client(df_inc, client)
    internal_email        = df_config["internal_email"].values[0]
    msgs                  = get_msgs(notif_msgs, company_name)

    mail_body  = notif_msgs["starting_msg"].format(client=client)

    mail_body += build_external_notif_expired(msgs, df_client, inv_notified_ext)
    mail_body += build_external_notif_to_expire(msgs, df_client, inv_notified_ext)
    mail_body += build_payment_methods(notif_msgs, df_config)

    mail_body += notif_msgs["no_response_warning"].format(internal_email=internal_email,company_name=company_name)
    mail_body += notif_msgs["ending_msg"].format(fili_web_url=fili_web_url)

    mail_data["body"]       = mail_body
    mail_data["subject"]    = msgs["subject"]
    mail_data["email_to"]   = utils.get_contact_mail_as_list(df_client)

    return mail_data


# ------------------------------------------------------------------------
# function:
#   build_external_notif_expired()
# ------------------------------------------------------------------------
def build_external_notif_expired(msgs, df_client, inv_notified_ext):
    body = ''

    df_due      = utils.get_due_invoices(df_client)

    if not df_due.empty:
        html_table      =  utils.get_df_as_external_html_table(df_due)
        html_table      =  utils.format_html_table(html_table, ext_expired=True)
        body            += msgs["greating"]
        body            += msgs["reminder"]
        body            += msgs["expired_msg"]
        body            += html_table
        body            += msgs["expired_instr"]

        [inv_notified_ext.append(id) for id in df_due.invoice_unique_key.values]

    return body

# ------------------------------------------------------------------------
# function:
#   build_external_notif_to_expire()
# ------------------------------------------------------------------------
def build_external_notif_to_expire(msgs, df_client, inv_notified_ext):
    body = ''

    limit_days          = utils.days_left_in_week()
    df_upcoming_inc     = utils.get_upcoming_invoices(df_client, limit_days)

    if not df_upcoming_inc.empty:
        html_table      =  utils.get_df_as_external_html_table(df_upcoming_inc)
        html_table      =  utils.format_html_table(html_table)
        body            += msgs["to_expire"]
        body            += html_table

        [inv_notified_ext.append(id) for id in df_upcoming_inc.invoice_unique_key.values]

    return body


# ------------------------------------------------------------------------
# function:
#   build_payment_methods()
# ------------------------------------------------------------------------
def build_payment_methods(notif_msgs, df_config):
    body = ''

    paymment_confirmation_msg = False

    if df_config["payment_gateway_interest"].values[0]:
        payment_link    = df_config["payment_link"].values[0]
        body            += notif_msgs["payment_link_msg"].format(payment_link=payment_link)
        paymment_confirmation_msg = True


    if df_config["payment_transfer_interest"].values[0]:
        bank                = df_config["payment_bank"].values[0]
        account_owner       = df_config["payment_account_owner"].values[0]
        alias_cbu           = df_config["payment_alias_cbu"].values[0]
        body                += notif_msgs["bank_information"].format(bank=bank, account_owner=account_owner, alias_cbu=alias_cbu)
        paymment_confirmation_msg = True

    if paymment_confirmation_msg:
        body            += notif_msgs["payment_confirmation_msg"]

    return body


# ------------------------------------------------------------------------
# function:
#   get_msgs()
# ------------------------------------------------------------------------
def get_msgs(notif_msgs, company_name):

    if utils.is_monday():
        day_msgs       = notif_msgs["first_week_contact"]
    else:
        day_msgs       = notif_msgs["second_week_contact"]

    subject         = day_msgs["subject"].format(company_name=company_name)
    greating        = day_msgs["greating"]
    reminder        = day_msgs["reminder"].format(company_name=company_name)
    expired_msg     = day_msgs["invoice_expired_msg"]
    expired_instr   = day_msgs["invoice_expired_instruction"]
    to_expire       = day_msgs["invoice_to_expire_msg"]

    msgs_dict = {  "subject"       : subject,
                    "greating"      : greating,
                    "reminder"      : reminder,
                    "expired_msg"   : expired_msg,
                    "expired_instr" : expired_instr,
                    "to_expire"     : to_expire}

    return msgs_dict

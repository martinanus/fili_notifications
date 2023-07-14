import utils
import numpy as np

# ------------------------------------------------------------------------
# function:
#   builf_external_notif()
# ------------------------------------------------------------------------
def build_external_notif(notif_msgs, df_config, df_inv, client, inv_notified_ext, company_name):
    mail_data  = {}

    df_inc                = utils.get_df_income(df_inv)
    df_client             = utils.get_inv_by_client(df_inc, client)

    msgs                  = get_msgs(notif_msgs, company_name)

    mail_body  = notif_msgs["starting_msg"].format(client=client)

    mail_body += build_external_notif_expired(msgs, df_client, inv_notified_ext)
    mail_body += build_external_notif_to_expire(msgs, df_client, inv_notified_ext)
    mail_body += build_payment_methods(notif_msgs, df_config)


    internal_email = df_config["internal_email"].values[0]
    fili_web_url   = "www.somosfili.com" #TODO - add fili web URL with campaign

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
def build_external_notif_expired(toned_msgs, df_client, inv_notified_ext):
    body = ''

    df_due      = utils.get_due_invoices(df_client)

    if not df_due.empty:
        html_table      =  utils.get_df_as_external_html_table(df_due)
        html_table      =  utils.format_html_table(html_table, ext_expired=True)
        body            += toned_msgs["greating"]
        body            += toned_msgs["reminder"]
        body            += toned_msgs["expired_msg"]
        body            += html_table
        body            += "<BR>"
        body            += toned_msgs["expired_instr"]

        [inv_notified_ext.append(id) for id in df_due.unique_key.values]

    return body

# ------------------------------------------------------------------------
# function:
#   build_external_notif_to_expire()
# ------------------------------------------------------------------------
def build_external_notif_to_expire(toned_msgs, df_client, inv_notified_ext):
    body = ''

    df_pre_exp  = utils.get_pre_exp_invoices(df_client)

    if not df_pre_exp.empty:
        html_table      =  utils.get_df_as_external_html_table(df_pre_exp)
        html_table      =  utils.format_html_table(html_table)
        body            += toned_msgs["to_expire"]
        body            += html_table
        body            += "<BR>"

        [inv_notified_ext.append(id) for id in df_pre_exp.unique_key.values]

    return body


# ------------------------------------------------------------------------
# function:
#   build_payment_methods()
# ------------------------------------------------------------------------
def build_payment_methods(notif_msgs, df_config):
    body = ''

    paymment_confirmation_msg = False


    if df_config.payment_gateway_interest[0] is True:
        payment_link = df_config.payment_link[0]
        body            += notif_msgs["payment_link_msg"].format(payment_link=payment_link)
        paymment_confirmation_msg = True


    if df_config.payment_transfer_interest[0] is True:
        bank                = df_config.payment_bank[0]
        account_owner       = df_config.payment_account_owner[0]
        alias               = df_config.payment_alias[0]

        body            += notif_msgs["payment_link_msg"].format(bank=bank, account_owner=account_owner, alias=alias)
        paymment_confirmation_msg = True

    if paymment_confirmation_msg is True:
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

    toned_dict = {  "subject"       : subject,
                    "greating"      : greating,
                    "reminder"      : reminder,
                    "expired_msg"   : expired_msg,
                    "expired_instr" : expired_instr,
                    "to_expire"     : to_expire}


    return toned_dict

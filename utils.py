import json
import re
import datetime
from pytz import timezone

# ------------------------------------------------------------------------
# function:
#   read_json_file()
# ------------------------------------------------------------------------
def read_json_file(path):

    f       = open(path)
    data    = json.load(f)
    f.close()

    return data

# ------------------------------------------------------------------------
# function:
#   get_df_as_internal_html_table()
# ------------------------------------------------------------------------
def get_df_as_internal_html_table(df):

    df['installment'] = df['installment_i'].map(str) + ' / ' + df['installment_total'].map(str)

    html_table = df.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email', 'installment'], justify='center', float_format='%.2f')

    return html_table

# ------------------------------------------------------------------------
# function:
#   get_df_as_external_html_table()
# ------------------------------------------------------------------------
def get_df_as_external_html_table(df):
    df['days_to_pay'] = df['days_to_pay'].abs()
    df['installment'] = df['installment_i'].map(str) + ' / ' + df['installment_total'].map(str)

    df['showable_inv_id'] = df['invoice_id'].map(str)
    df.loc[df['upload_source'] == 'manual', 'showable_inv_id'] = '-'

    html_table = df.to_html(columns=['showable_inv_id', 'amount', 'due_date', 'days_to_pay', 'installment'], justify='center', float_format='%.2f')

    return html_table

# ------------------------------------------------------------------------
# function:
#   format_html_table()
# ------------------------------------------------------------------------
def format_html_table(table, ext_expired=False):
    table = table.replace('counterpart', 'Cliente')
    table = table.replace('amount', 'Monto ($)')
    table = table.replace('invoice_id', 'ID factura')
    table = table.replace('showable_inv_id', 'ID factura')
    table = table.replace('due_date', 'Fecha de vencimiento')
    table = table.replace('contact_email', 'E-mail')
    table = table.replace('installment', 'N° de cuota')

    if ext_expired:
        table = table.replace('days_to_pay', 'Días de atraso')
    else:
        table = table.replace('days_to_pay', 'Días hasta el vencimiento')


    return table

# ------------------------------------------------------------------------
# function:
#   get_days_as_list()
# ------------------------------------------------------------------------
def get_days_as_list(df_config, column, neg_list=False):
    vals            = df_config[column].values[-1]
    if (vals is None) or (vals[0:7] is 'Ninguna'):
        return []
    vals_trim       = re.sub("[^0-9,-]", "", vals)
    str_l           = re.split(',|-', vals_trim)
    str_l_no_empty  = [i for i in str_l if i]
    if 'Día del vencimiento' in vals:
        str_l_no_empty.append('0')

    list_int = [int(i) for i in str_l_no_empty]

    if neg_list:
        list_int = [-i for i in list_int]

    if is_monday():
        list_int = append_two_prev_days(list_int, neg_list)

    return list_int

# ------------------------------------------------------------------------
# function:
#   get_internal_mails_as_list()
# ------------------------------------------------------------------------
def get_internal_mails_as_list(df_config):
    vals            = df_config["internal_email"].values[-1]
    if (vals is None) or ('@' not in vals) or ('.' not in vals):
        return []
    str_l           = vals.split(',')
    str_l_no_empty  = [i for i in str_l if i]

    return str_l_no_empty

# ------------------------------------------------------------------------
# function:
#   get_contact_mail_as_list()
# ------------------------------------------------------------------------
def get_contact_mail_as_list(df_client):
    vals            = df_client["contact_email"].values[-1]
    if (vals is None) or ('@' not in vals) or ('.' not in vals):
        return []
    str_l           = vals.split(',')
    str_l_no_empty  = [i for i in str_l if i]
    contact_mail_l  = [str_l_no_empty[0]]

    return contact_mail_l

# ------------------------------------------------------------------------
# function:
#   get_highest_value_in_list()
# ------------------------------------------------------------------------
def get_highest_value_in_list(list_str):
    list_int = [int(i) for i in list_str]
    list_int.sort(reverse=True)
    if not list_int:
        return ''

    return str(list_int[0])

# ------------------------------------------------------------------------
# function:
#   is_monday()
# ------------------------------------------------------------------------
def is_monday():
    tz       = timezone('America/Argentina/Buenos_Aires')
    now      = datetime.datetime.now(tz)
    weekday  = now.weekday()

    return (weekday is 0)

# ------------------------------------------------------------------------
# function:
#   append_two_prev_days()
# ------------------------------------------------------------------------
def append_two_prev_days(day_l, neg_list=False):
    app_list = []

    for day in day_l:
        app_list.append(day)
        app_list.append(day-1)
        app_list.append(day-2)

    if not neg_list:
        app_list = [day for day in app_list if (day >= 0)]
    else:
        app_list = [day for day in app_list if (day < 0)]

    return app_list


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

# ------------------------------------------------------------------------
# function:
#   get_total_debt()
# ------------------------------------------------------------------------
def get_total_debt(df_client):
    total_debt = df_client.amount.sum()
    return total_debt

# ------------------------------------------------------------------------
# function:
#   get_due_debt()
# ------------------------------------------------------------------------
def get_due_debt(df_client):
    df_client = df_client[(df_client.days_to_pay<0)]
    due_debt = df_client.amount.sum()
    return due_debt

# ------------------------------------------------------------------------
# function:
#   get_to_expire_debt()
# ------------------------------------------------------------------------
def get_to_expire_debt(df_client):
    df_client = df_client[(df_client.days_to_pay>=0)]
    to_expire_debt = df_client.amount.sum()
    return to_expire_debt

# ------------------------------------------------------------------------
# function:
#   get_oldest_unique_key()
# ------------------------------------------------------------------------
def get_oldest_unique_key(df_client):
    df_client = df_client[(df_client.days_to_pay<0)]
    df_client = df_client.sort_values(by='days_to_pay', ascending=True).reset_index()
    oldest_unique_key = df_client.unique_key.values[0]
    return oldest_unique_key

# ------------------------------------------------------------------------
# function:
#   get_oldest_invoice_date()
# ------------------------------------------------------------------------
def get_oldest_invoice_date(df_client):
    df_client = df_client[(df_client.days_to_pay<0)]
    df_client = df_client.sort_values(by='days_to_pay', ascending=True).reset_index()
    oldest_invoice_date = df_client.due_date.values[0]
    return oldest_invoice_date


# ------------------------------------------------------------------------
# function:
#   get_clients_to_notify()
# ------------------------------------------------------------------------
def get_clients_to_notify(df_config, df_inv):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif_collect", neg_list=True)
    external_notif_days          = external_pre_notif_days + external_post_notif_days

    df = df_inv[(df_inv.relation=='Cliente') &
                (df_inv.days_to_pay.isin(external_notif_days)) &
                (df_inv.notification_status_ext!='exclude')]

    clients = df['counterpart'].unique()

    return clients


# ------------------------------------------------------------------------
# function:
#   get_external_inv_to_notify()
# ------------------------------------------------------------------------
def get_external_inv_to_notify(df_config, df_inv):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif_collect", neg_list=True)
    external_notif_days         = external_pre_notif_days + external_post_notif_days

    df = df_inv[(df_inv.relation=='Cliente') &
                (df_inv.days_to_pay.isin(external_notif_days)) &
                (df_inv.notification_status_ext!='exclude')]

    return df

# ------------------------------------------------------------------------
# function:
#   get_inv_to_notify_by_client()
# ------------------------------------------------------------------------
def get_inv_to_notify_by_client(df_inv, client, external_notif_days):
    df_client = df_inv[(df_inv.relation=='Cliente') &
                (df_inv.counterpart==client) &
                (df_inv.notification_status_ext!='exclude') &
                ((df_inv.days_to_pay.isin(external_notif_days)) | (df_inv.notification_status_ext!='non_notified'))]
    return df_client


# ------------------------------------------------------------------------
# function:
#   get_due_invoices()
# ------------------------------------------------------------------------
def get_due_invoices(df_in):
    df_out = df_in[(df_in.days_to_pay < 0)]
    df_out = df_out.sort_values(by='days_to_pay', ascending=True).reset_index()
    return df_out

# ------------------------------------------------------------------------
# function:
#   get_pre_exp_invoices()
# ------------------------------------------------------------------------
def get_pre_exp_invoices(df_in):
    df_out = df_in[(df_in.days_to_pay >= 0)]
    df_out = df_out.sort_values(by='days_to_pay', ascending=True).reset_index()
    return df_out

# ------------------------------------------------------------------------
# function:
#   get_total_amout()
# ------------------------------------------------------------------------
def get_total_amout(df_in):
    total_amount = df_in.amount.sum()
    return total_amount


# ------------------------------------------------------------------------
# function:
#   get_external_notification_days()
# ------------------------------------------------------------------------
def get_external_notification_days(df_config):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif_collect", neg_list=True)
    external_notif_days          = external_pre_notif_days + external_post_notif_days
    return external_notif_days

# ------------------------------------------------------------------------
# function:
#   get_max_day_pre_notif_config()
# ------------------------------------------------------------------------
def get_max_day_pre_notif_config(df_config):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
    max_day_pre_notif_config = get_highest_value_in_list(external_pre_notif_days)
    return max_day_pre_notif_config

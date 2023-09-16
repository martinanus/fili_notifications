import json
import re
import datetime
from pytz import timezone
import pandas as pd
import numpy as np

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
#   merge_crm_data()s
# ------------------------------------------------------------------------
def merge_crm_data(df_inv, df_crm):
    return pd.merge(df_inv, df_crm, on=["counterpart"], suffixes=('_inv', ''))



# ------------------------------------------------------------------------
# function:
#   preformat_df_to_html_table()
# ------------------------------------------------------------------------
def preformat_df_to_html_table(df, crm_data):
    df.loc[df['currency'] == "peso", 'currency']            = '$'
    df.loc[df['currency'] == "dollar_official", 'currency'] = 'USD'
    df.loc[df['currency'] == "dollar_blue", 'currency']     = 'USD'
    df.loc[df['currency'] == "dollar_mep", 'currency']      = 'USD'

    df['amount_currency'] = df['currency'].map(str) + ' ' + df['amount'].map(str)

    df['showable_url'] = '<a href="'+ df['url_invoice'].map(str) +'"> Click aquí</a>'

    df.loc[df['url_invoice'].isnull(), 'showable_url'] = '-'
    df.loc[df['contact_email'].isnull(), 'contact_email'] = '-'

    if crm_data:
        df.loc[df['payment_bank'].isnull(), 'payment_bank'] = '-'
        df.loc[df['payment_alias_cbu'].isnull(), 'payment_alias_cbu'] = '-'
        df.loc[df['cuit'].isnull(), 'cuit'] = '-'



    df.index = np.arange(1, len(df) + 1)

    df['installment'] = df['installment_i'].map(str) + ' / ' + df['installment_total'].map(str)
    df = format_date_column(df, 'due_date')

    amount_str = []
    [amount_str.append("{:,.2f}".format(f)) for f in df['amount']]
    df['amount'] = amount_str

    df['days_to_pay'] = df['days_to_pay'].abs().astype({'days_to_pay':'int'})


    return df


# ------------------------------------------------------------------------
# function:
#   get_df_as_daily_due_payment_html_table()s
# ------------------------------------------------------------------------
def get_df_as_daily_due_payment_html_table(df):

    df_formatted = preformat_df_to_html_table(df, crm_data=True)

    html_table = df_formatted.to_html(columns=['counterpart', 'amount_currency', 'payment_bank',
                                     'payment_alias_cbu', 'cuit', 'contact_email',
                                      'showable_url' ], justify='center', float_format='%.2f')

    html_table = html_table.replace('&lt;', '<')
    html_table = html_table.replace('&gt;', '>')

    return html_table

# ------------------------------------------------------------------------
# function:
#   get_df_as_daily_due_receipt_html_table()
# ------------------------------------------------------------------------
def get_df_as_daily_due_receipt_html_table(df):

    df_formatted = preformat_df_to_html_table(df, crm_data=True)


    html_table = df_formatted.to_html(columns=['counterpart', 'amount_currency', 'contact_email',
                                      'showable_url' ], justify='center', float_format='%.2f')

    html_table = html_table.replace('&lt;', '<')
    html_table = html_table.replace('&gt;', '>')

    return html_table


# ------------------------------------------------------------------------
# function:
#   get_df_as_internal_html_table()s
# ------------------------------------------------------------------------
def get_df_as_internal_html_table(df):

    df_formatted = preformat_df_to_html_table(df, crm_data=False)

    html_table = df_formatted.to_html(columns=['counterpart', 'amount_currency', 'invoice_id', 'due_date', 'contact_email', 'installment', 'showable_url'], justify='center', float_format='%.2f')

    html_table = html_table.replace('&lt;', '<')
    html_table = html_table.replace('&gt;', '>')

    return html_table

# ------------------------------------------------------------------------
# function:
#   get_df_as_external_html_table()
# ------------------------------------------------------------------------
def get_df_as_external_html_table(df):
    df_formatted = preformat_df_to_html_table(df, crm_data=False)


    df_formatted = format_date_column(df, 'due_date')


    html_table = df_formatted.to_html(columns=['showable_inv_id', 'amount_currency', 'due_date', 'days_to_pay', 'installment'], justify='center', float_format='%.2f')

    return html_table

# ------------------------------------------------------------------------
# function:
#   format_html_table()
# ------------------------------------------------------------------------
def format_html_table(table, ext_expired=False):
    table = table.replace('counterpart', 'Contraparte')
    table = table.replace('amount_currency', 'Monto')
    table = table.replace('invoice_id', 'ID')
    table = table.replace('showable_inv_id', 'ID factura')
    table = table.replace('due_date', 'Fecha de vencimiento')
    table = table.replace('contact_email', 'E-mail')
    table = table.replace('installment', 'N° de cuota')
    table = table.replace('showable_url', 'Factura adjunta')
    table = table.replace('payment_bank', 'Banco')
    table = table.replace('payment_alias_cbu', 'Alias/CBU')
    table = table.replace('cuit', 'CUIT')


    if ext_expired:
        table = table.replace('days_to_pay', 'Días de atraso')
    else:
        table = table.replace('days_to_pay', 'Días hasta el vencimiento')

    table += "<BR>"

    return table

# ------------------------------------------------------------------------
# function:
#   get_days_as_list()
# ------------------------------------------------------------------------
def get_days_as_list(df_config, column, neg_list=False):
    vals            = df_config[column].values[0]
    if (vals is None) or (vals[0:7] == 'Ninguna'):
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
    vals            = df_config["internal_email"].values[0]
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
    vals            = df_client["contact_email"].values[0]
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

    return (weekday == 0)

# ------------------------------------------------------------------------
# function:
#   is_thursday()
# ------------------------------------------------------------------------
def is_thursday():
    tz       = timezone('America/Argentina/Buenos_Aires')
    now      = datetime.datetime.now(tz)
    weekday  = now.weekday()

    return (weekday == 4)

# ------------------------------------------------------------------------
# function:
#   days_left_in_week()
# ------------------------------------------------------------------------
def days_left_in_week():
    tz       = timezone('America/Argentina/Buenos_Aires')
    now      = datetime.datetime.now(tz)
    weekday  = now.weekday()

    return (7 - weekday)

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
#   get_inv_in_days()
# ------------------------------------------------------------------------
def get_inv_in_days(df_inv, days, is_income, is_pre):
    if is_pre:
        df                  = df_inv[(df_inv.is_income==is_income) &
                                ( (df_inv.days_to_pay.isin(days) |
                                ( (df_inv.notification_status_int=='notified') & (df_inv.days_to_pay >= 0)))) ]
    else:
        df                  = df_inv[(df_inv.is_income==is_income) &
                                ( (df_inv.days_to_pay.isin(days) |
                                ( (df_inv.notification_status_int=='notified') & (df_inv.days_to_pay < 0)))) ]
    df                  = df.sort_values(by='days_to_pay', ascending=True).reset_index()

    return df

# ------------------------------------------------------------------------
# function:
#   get_df_income()
# ------------------------------------------------------------------------
def get_df_income(df_in):
    df_out = df_in[df_in.is_income==True].reset_index()
    return df_out

# ------------------------------------------------------------------------
# function:
#   get_df_outcome()
# ------------------------------------------------------------------------
def get_df_outcome(df_in):
    df_out = df_in[df_in.is_income==False].reset_index()
    return df_out

# ------------------------------------------------------------------------
# function:
#   get_upcoming_invoices()
# ------------------------------------------------------------------------
def get_upcoming_invoices(df_in, limit_days):
    df_out = df_in[(df_in.days_to_pay >= 0) &
                   (df_in.days_to_pay <= limit_days)  ]

    df_out = df_out.sort_values(by='days_to_pay', ascending=True).reset_index()

    return df_out

# ------------------------------------------------------------------------
# function:
#   get_today_due_invoices()
# ------------------------------------------------------------------------
def get_today_due_invoices(df_in):
    df_out = get_upcoming_invoices(df_in, 0)
    return df_out

# ------------------------------------------------------------------------
# function:
#   get_periodicity_in_days()
# ------------------------------------------------------------------------
def get_periodicity_in_days(df_config):
    periodicity = df_config["internal_periodicity"].values[0]
    if periodicity == "Semanalmente":
        days = 7
    elif periodicity == "Quincenalmente":
        days = 15
    elif periodicity == "Mensualmente":
        days = 30
    else:
        days = -1

    return days

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
#   get_oldest_invoice_unique_key()
# ------------------------------------------------------------------------
def get_oldest_invoice_unique_key(df_client):
    df_client = df_client.sort_values(by='days_to_pay', ascending=True).reset_index()
    oldest_invoice_unique_key = df_client.invoice_unique_key[0]
    return oldest_invoice_unique_key

# ------------------------------------------------------------------------
# function:
#   get_oldest_invoice_date()
# ------------------------------------------------------------------------
def get_oldest_invoice_date(df_client):
    df_client = df_client.sort_values(by='days_to_pay', ascending=True).reset_index()
    oldest_invoice_date = df_client.due_date[0]
    oldest_invoice_date = pd.to_datetime(oldest_invoice_date).strftime("%d-%m-%Y")
    return oldest_invoice_date

# ------------------------------------------------------------------------
# function:
#   get_external_inv_to_notify()
# ------------------------------------------------------------------------
def get_external_inv_to_notify(df_config, df_inv):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif", neg_list=True)
    external_notif_days         = external_pre_notif_days + external_post_notif_days

    df = df_inv[(df_inv.is_income==True) &
                (df_inv.days_to_pay.isin(external_notif_days)) &
                (df_inv.notification_status_ext!='exclude')]

    return df

# ------------------------------------------------------------------------
# function:
#   get_inv_to_notify_by_client()
# ------------------------------------------------------------------------
def get_inv_to_notify_by_client(df_inv, client, external_notif_days):
    df_client = df_inv[(df_inv.is_income==True) &
                (df_inv.counterpart==client) &
                (df_inv.notification_status_ext!='exclude') &
                ((df_inv.days_to_pay.isin(external_notif_days)) | (df_inv.notification_status_ext!='non_notified'))]
    return df_client

# ------------------------------------------------------------------------
# function:
#   get_inv_to_notify_by_client()
# ------------------------------------------------------------------------
def get_inv_by_client(df_inv, client):
    df_client = df_inv[(df_inv.counterpart==client)]
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
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif", neg_list=True)
    external_notif_days          = external_pre_notif_days + external_post_notif_days
    return external_notif_days

# ------------------------------------------------------------------------
# function:
#   get_max_day_pre_notif_config()
# ------------------------------------------------------------------------
def get_max_day_pre_notif_config(df_config):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif")
    max_day_pre_notif_config = get_highest_value_in_list(external_pre_notif_days)
    return max_day_pre_notif_config

# ------------------------------------------------------------------------
# function:
#   format_date_column()
# ------------------------------------------------------------------------
def format_date_column(df_inv, col):
    df_inv[col] = pd.to_datetime(df_inv[col])
    df_inv[col] = df_inv[col].dt.strftime("%d-%m-%Y")
    df_inv[col] = df_inv[col].str.replace('-01-', '-Ene-')
    df_inv[col] = df_inv[col].str.replace('-02-', '-Feb-')
    df_inv[col] = df_inv[col].str.replace('-03-', '-Mar-')
    df_inv[col] = df_inv[col].str.replace('-04-', '-Abr-')
    df_inv[col] = df_inv[col].str.replace('-05-', '-May-')
    df_inv[col] = df_inv[col].str.replace('-06-', '-Jun-')
    df_inv[col] = df_inv[col].str.replace('-07-', '-Jul-')
    df_inv[col] = df_inv[col].str.replace('-08-', '-Ago-')
    df_inv[col] = df_inv[col].str.replace('-09-', '-Sep-')
    df_inv[col] = df_inv[col].str.replace('-10-', '-Oct-')
    df_inv[col] = df_inv[col].str.replace('-11-', '-Nov-')
    df_inv[col] = df_inv[col].str.replace('-12-', '-Dic-')

    return df_inv

# ------------------------------------------------------------------------
# function:
#   add_utm_to_link()
# ------------------------------------------------------------------------
def add_utm_to_link(link, source, medium, campaign, content=False):


    url_with_utm = link+"?utm_source="+source+"&utm_medium="+medium+"&utm_campaign="+campaign

    if content is not False:
        url_with_utm += "&utm_content="+content

    url_with_utm_no_space = url_with_utm.replace(" ", "_")

    return url_with_utm_no_space

# ------------------------------------------------------------------------
# function:
#   hash_str()
# ------------------------------------------------------------------------
def hash_str(str_to_hash):
    return str(sum([ord(c) for c in str_to_hash])*ord(str_to_hash[0]))


# ------------------------------------------------------------------------
# function:
#   get_clients_to_notify()
# ------------------------------------------------------------------------
def get_clients_to_notify(df_inv):

    df_inc              = get_df_income(df_inv)
    df_due_inc          = get_due_invoices(df_inc)

    limit_days          = days_left_in_week()
    df_upcoming_inc     = get_upcoming_invoices(df_inc, limit_days)


    df      = df_due_inc.append(df_upcoming_inc)

    clients = df['counterpart'].unique()

    return clients
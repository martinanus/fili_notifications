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
#   get_df_as_html_table()
# ------------------------------------------------------------------------
def get_df_as_html_table(df):
    html_table = df.to_html(columns=['counterpart', 'amount', 'invoice_id', 'due_date', 'contact_email'], justify='center')

    return html_table

# ------------------------------------------------------------------------
# function:
#   format_html_table()
# ------------------------------------------------------------------------
def format_html_table(table):
    table = table.replace('counterpart', 'Cliente')
    table = table.replace('amount', 'Monto ($)')
    table = table.replace('invoice_id', 'ID factura')
    table = table.replace('due_date', 'Fecha de vencimiento')
    table = table.replace('contact_email', 'E-mail')

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
#   get_mails_as_list()
# ------------------------------------------------------------------------
def get_mails_as_list(df_config):
    vals            = df_config["internal_email"].values[-1]
    if (vals is None) or ('@' not in vals) or ('.' not in vals):
        return []
    str_l           = vals.split(',')
    str_l_no_empty  = [i for i in str_l if i]

    return str_l_no_empty

# ------------------------------------------------------------------------
# function:
#   get_mails_as_list()
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

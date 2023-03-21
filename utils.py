import json
import re

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
#   format_html_table(table)
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
#   get_days_as_list(df_config, column)
# ------------------------------------------------------------------------
def get_days_as_list(df_config, column):
    vals            = df_config[column].values[-1]
    if (vals is None) or (vals[0:7] is 'Ninguna'):
        return []
    vals_trim       = re.sub("[^0-9,-]", "", vals)
    str_l           = re.split(',|-', vals_trim)
    str_l_no_empty  = [i for i in str_l if i]
    if 'Día del vencimiento' in vals:
        str_l_no_empty.append('0')

    return str_l_no_empty

# ------------------------------------------------------------------------
# function: 
#   get_mails_as_list(df_config)
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
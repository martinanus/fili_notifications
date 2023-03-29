from google.cloud import bigquery
from google.oauth2 import service_account
import re
import datetime
from pytz import timezone

def get_client():
    credentials = service_account.Credentials.from_service_account_file(
        "credentials.json", scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client_bq = bigquery.Client(credentials=credentials, project=credentials.project_id,)
    return client_bq

client = get_client()

def get_configuration(client):
    query = """
    SELECT *
    FROM `fili-377220.fili_sandbox.bq_notification_config`"""
    query_job       = client.query(query)  # Make an API request.
    result          = query_job.result()
    df              = result.to_dataframe()
    df              = df.sort_values(by='timestamp', ascending=True)
    return df

def get_pending_invoices(client):
    query = """
    SELECT relation, counterpart, amount, invoice_id, due_date, contact_email, days_to_pay, notification_status_int, notification_status_ext
    FROM `fili-377220.fili_sandbox.invoices`
    WHERE status!='aprobada'"""
    query_job       = client.query(query)
    result          = query_job.result()
    df              = result.to_dataframe()
    return df

def is_monday():
    tz       = timezone('America/Argentina/Buenos_Aires')
    now      = datetime.datetime.now(tz)
    weekday  = now.weekday()
    return (weekday is 0)

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

def append_two_prev_days(day_l, neg_list=False):
    app_list = []
    for day in day_l:
        app_list.append(day)
        app_list.append(day+1)
        app_list.append(day+2)
    if neg_list:
        app_list = [day for day in app_list if (day < 0)]
    return app_list



def get_clients_to_notify(df_config, df_inv):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif_collect", neg_list=True)
    external_notif_days         = external_pre_notif_days + external_post_notif_days
    df = df_inv[(df_inv.relation=='Cliente') & (df_inv.days_to_pay.isin(external_notif_days))]
    clients = df['counterpart'].unique()
    return clients


def get_total_debt(client, df_inv):
    total_debt = 0.0
    df_client = df_inv[(df_inv.relation=='Cliente') & (df_inv.counterpart==client)]
    for index, row in df_client.iterrows():
        total_debt += row.amount
    return total_debt

def get_due_debt(client, df_inv):
    due_debt = 0.0
    df_client = df_inv[(df_inv.relation=='Cliente') & (df_inv.counterpart==client)
                       & (df_inv.days_to_pay<0)]
    for index, row in df_client.iterrows():
        due_debt += row.amount
    return due_debt

def get_clients_to_notify(df_config, df_inv):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif_collect", neg_list=True)
    external_notif_days          = external_pre_notif_days + external_post_notif_days
    df = df_inv[(df_inv.relation=='Cliente') &
                (df_inv.days_to_pay.isin(external_notif_days)) &
                (df_inv.notification_status_ext!='exclude')]
    clients = df['counterpart'].unique()
    return clients

def get_external_inv_to_notify(df_config, df_inv):
    external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
    external_post_notif_days     = get_days_as_list(df_config, "external_post_notif_collect", neg_list=True)
    external_notif_days         = external_pre_notif_days + external_post_notif_days
    df = df_inv[(df_inv.relation=='Cliente') &
                (df_inv.days_to_pay.isin(external_notif_days)) &
                (df_inv.notification_status_ext!='exclude')]
    return df


def get_inv_to_notify_by_client(df_inv, client, external_notif_days):
    df = df_inv[(df_inv.relation=='Cliente') &
                (df_inv.counterpart==client) &
                (df_inv.notification_status_ext!='exclude') &
                ((df_inv.days_to_pay.isin(external_notif_days)) | (df_inv.notification_status_ext!='non_notified'))]
    return df

def get_due_invoices(df_in):
    df_out = df_in[(df_in.days_to_pay < 0)]
    df_out = df_out.sort_values(by='days_to_pay', ascending=True).reset_index()
    return df_out

def get_pre_exp_invoices(df_in):
    df_out = df_in[(df_in.days_to_pay >= 0)]
    df_out = df_out.sort_values(by='days_to_pay', ascending=True).reset_index()
    return df_out

def get_total_amout(df_in):
    total_amount = df_in.amount.sum()
    return total_amount



df_config = get_configuration(client)
df_inv    = get_pending_invoices(client)

external_pre_notif_days      = get_days_as_list(df_config, "external_pre_notif_collect")
external_post_notif_days     = get_days_as_list(df_config, "external_post_notif_collect", neg_list=True)
external_notif_days         = external_pre_notif_days + external_post_notif_days

clients_to_notify = get_clients_to_notify(df_config, df_inv)

for client_not in clients_to_notify:
    df_client = get_inv_to_notify_by_client(df_inv, client_not, external_notif_days)
    df_client = df_client[["counterpart", "invoice_id", "amount", "days_to_pay", "notification_status_ext"]]
    print(df_client)
    df_due      = get_due_invoices(df_client)
    print(df_due)
    df_pre_exp  = get_pre_exp_invoices(df_client)
    print(df_pre_exp)
    total_debt  = get_total_amout(df_client)
    print("Total debt: ", total_debt)
    due_debt    = get_total_amout(df_due)
    print("Due debt: ", due_debt)



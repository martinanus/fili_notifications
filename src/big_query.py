from google.cloud import bigquery
from google.oauth2 import service_account

# ------------------------------------------------------------------------
# function:
#   get_client()
# ------------------------------------------------------------------------
def get_client(key_path):
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client_bq = bigquery.Client(credentials=credentials, project=credentials.project_id,)

    return client_bq

# ------------------------------------------------------------------------
# function:
#   get_configuration()
# ------------------------------------------------------------------------
def get_configuration(table_id, bq_client):
    query = """
    SELECT *
    FROM `"""+ table_id + """`"""

    query_job       = bq_client.query(query)  # Make an API request.
    result          = query_job.result()
    df              = result.to_dataframe()
    df              = df.sort_values(by='timestamp', ascending=False).reset_index()
    df              = df.filter(items=[0], axis=0)

    return df


# ------------------------------------------------------------------------
# function:
#   get_pending_invoices()
# ------------------------------------------------------------------------
def get_pending_invoices(table_id, bq_client):

    query = """
    SELECT url_invoice, is_income, counterpart, currency, amount, invoice_id, invoice_unique_key, due_date, contact_email, days_to_pay,
            notification_status_int, notification_status_ext, installment_i, installment_total, is_invoice
    FROM `""" + table_id + """`
    WHERE invoice_payment_relation='invoice' """

    query_job       = bq_client.query(query)
    result          = query_job.result()
    df              = result.to_dataframe()

    return df

# ------------------------------------------------------------------------
# function:
#   update_notification_status()
# ------------------------------------------------------------------------
def update_notification_status(table_id, field, bq_client, inv_notified):

    invoices_id = ','.join([("'"+(str(i))+"'") for i in inv_notified])

    query = """
    UPDATE `""" + table_id + """`
    SET     """ + field    +""" = 'notified'
    WHERE   unique_key in  (""" + invoices_id + """);"""

    query_job       = bq_client.query(query)
    query_job.result()
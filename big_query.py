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
    df              = df.sort_values(by='timestamp', ascending=True)

    return df


# ------------------------------------------------------------------------
# function:
#   get_pending_invoices()
# ------------------------------------------------------------------------
def get_pending_invoices(table_id, bq_client):

    query = """
    SELECT relation, counterpart, amount, invoice_id, unique_key, due_date, contact_email, days_to_pay,
            notification_status_int, notification_status_ext, installment_i, installment_total, upload_source
    FROM `""" + table_id + """`
    WHERE status!='aprobada'"""

    query_job       = bq_client.query(query)
    result          = query_job.result()
    df              = result.to_dataframe()

    return df


# ------------------------------------------------------------------------
# function:
#   update_notification_status_int()
# ------------------------------------------------------------------------
def update_notification_status_int(table_id, bq_client, inv_notified_int):

    invoices_id = ','.join([str(i) for i in inv_notified_int])

    query = """
    UPDATE `""" + table_id + """`
    SET   notification_status_int='notified'
    WHERE unique_key in (""" + invoices_id + """)"""

    bq_client.query(query)

# ------------------------------------------------------------------------
# function:
#   update_notification_status_ext()
# ------------------------------------------------------------------------
def update_notification_status_ext(table_id, bq_client, inv_notified_ext):

    invoices_id = ','.join([str(i) for i in inv_notified_ext])

    query = """
    CREATE OR REPLACE TABLE   `""" + table_id + """` AS
    SELECT
    timestamp,
    counterpart,
    relation,
    invoice_id,
    installment_total,
    fixcost_total,
    fixcost_periodicity,
    installment_periodicity,
    invoice_date,
    approved_date,
    pay_delay,
    contact_email,
    url_invoice,
    status,
    notification_status_int,
    fixcost_i,
    installment_i,
    due_date,
    amount,
    days_to_pay,
    unique_key,
    CASE
        WHEN days_to_pay > -1 AND unique_key IN (""" + invoices_id + """) THEN "notified_0"
        WHEN days_to_pay < 0 AND days_to_pay > -21 AND unique_key IN (""" + invoices_id + """) THEN "notified_1"
        WHEN days_to_pay < -20 AND days_to_pay > -51 AND unique_key IN (""" + invoices_id + """) THEN "notified_2"
        WHEN days_to_pay < -50 AND days_to_pay > -81 AND unique_key IN (""" + invoices_id + """) THEN "notified_3"
        WHEN days_to_pay < -80 AND unique_key IN (""" + invoices_id + """) THEN "notified_4"
    ELSE
        notification_status_ext
    END AS notification_status_ext,
    upload_source
    FROM
    `""" + table_id + """`"""

    bq_client.query(query)
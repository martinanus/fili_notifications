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
def get_configuration(table_id, client):
    query = """
    SELECT *
    FROM `"""+ table_id + """`"""

    query_job       = client.query(query)  # Make an API request.
    result          = query_job.result()
    df              = result.to_dataframe()
    df              = df.sort_values(by='timestamp', ascending=True)

    return df


# ------------------------------------------------------------------------
# function: 
#   get_pending_invoices()
# ------------------------------------------------------------------------
def get_pending_invoices(table_id, client):
    
    query = """
    SELECT relation, counterpart, amount, invoice_id, due_date, contact_email, days_to_pay, notification_status
    FROM `""" + table_id + """`
    WHERE status!='aprobada'"""

    query_job       = client.query(query)  
    result          = query_job.result()
    df              = result.to_dataframe()
    
    return df


# ------------------------------------------------------------------------
# function: 
#   update_notification_status()
# ------------------------------------------------------------------------
def update_notification_status(table_id, client, inv_notified):
    
    invoices_id = ','.join([str(i) for i in inv_notified])

    query = """
    UPDATE `""" + table_id + """`
    SET   notification_status='notified'
    WHERE invoice_id in (""" + invoices_id + """)"""

    client.query(query)  
    
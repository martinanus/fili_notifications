# Library imports
import functions_framework
import requests

# File imports
import trigger_logic as trig
import internal_notif_build as inb
import external_notif_build as enb
import big_query as bq
import utils
import smtp


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------
key_path                    = "credentials.json"
internal_notif_msgs_path    = "internal_notif_msgs.json"
external_notif_msgs_path    = "external_notif_msgs.json"
smtp_sender                 = "soporte@somosfili.com"
smtp_password               = "pauoevdyxnwxqbvq"
db_request                     = {'args' : {
                                    'company_name':'sandbox',
                                    'dataset_name': 'fili_sandbox',
                                    'looker_config_link': 'https://lookerstudio.google.com/u/0/reporting/6d0fee52-f9c6-495c-b7a1-c778a83a29c0/page/p_hsqtmpj82c'
                                        }
                                }

# ------------------------------------------------------------------------
# function:
#   main()
# ------------------------------------------------------------------------
@functions_framework.http
def main(request):
    if request is 'db':
        request_args = db_request["args"]
        print("Debug mode")
    else:
        request_args = request.get_json(silent=True)
        if request_args is None:
            return "Error 400 Bad request - No json arguments detected "

    company_name                = request_args["company_name"]
    dataset_name                = request_args["dataset_name"]
    looker_config_link          = request_args["looker_config_link"]
    notif_table_id              = "fili-377220.{0}.bq_notification_config".format(dataset_name)
    invoice_table_id            = "fili-377220.{0}.invoices".format(dataset_name)
    print("\
            company name          : {0} \n\
            dataset               : {1} \n\
            looker_config_link    : {2} \n"
            .format(company_name, dataset_name, looker_config_link))


    bq_client               = bq.get_client(key_path)
    df_config               = bq.get_configuration(notif_table_id, bq_client)
    df_inv                  = bq.get_pending_invoices(invoice_table_id, bq_client)
    internal_notif_msgs     = utils.read_json_file(internal_notif_msgs_path)
    external_notif_msgs     = utils.read_json_file(external_notif_msgs_path)
    inv_notified_int        = []
    inv_notified_ext        = []

    if trig.trigger_receipt_notif(df_config, df_inv):
        internal_receipt_mail = inb.build_internal_receipt_notif(internal_notif_msgs, df_config, df_inv, inv_notified_int, looker_config_link)
        smtp.send_email_smtp(internal_receipt_mail, smtp_sender, smtp_password)
        print("Receipt notification triggered")
    else:
        print("Receipt notification not triggered")


    if trig.trigger_payement_notif(df_config, df_inv):
        internal_payements_mail  = inb.build_internal_payements_notif(internal_notif_msgs, df_config, df_inv, inv_notified_int)
        smtp.send_email_smtp(internal_payements_mail, smtp_sender, smtp_password)
        print("Payement notification triggered")
    else:
        print("Payement notification not triggered")

    if inv_notified_int:
        bq.update_notification_status_int(invoice_table_id, bq_client, inv_notified_int)
        print("Internal notification status has been updated in BQ")


    clients_to_notify = trig.get_clients_to_notify(df_config, df_inv)
    for client in clients_to_notify:
        external_mail = enb.build_external_notif(external_notif_msgs, df_config, df_inv, client, inv_notified_ext, company_name)
        smtp.send_email_smtp(external_mail, smtp_sender, smtp_password)
        print("\nExternal notification sent to ", client)

    if inv_notified_ext:
        bq.update_notification_status_ext(invoice_table_id, bq_client, inv_notified_ext)
        print("External notification status has been updated in BQ")

    return "Las notificaciones fueron enviadas!"


# # ------------------------------------------------------------------------
# #   Trigger main function execution when this file is run
# # ------------------------------------------------------------------------
if __name__ == "__main__":
    main('db')
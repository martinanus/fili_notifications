# Library imports
import functions_framework
import requests
from http import HTTPStatus

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
smtp_password               = "ssoxfgtuaurhtopd"
db_request                     = {'args' : {
                                    'company_name':'sandbox',
                                    'dataset_name': 'fili_sandbox',
                                    'looker_config_link': 'https://lookerstudio.google.com/reporting/4b0c66d1-c215-483c-ba4f-bc03f4c93659/page/p_hsqtmpj82c'
                                        }
                                }

# ------------------------------------------------------------------------
# function:
#   main()
# ------------------------------------------------------------------------
@functions_framework.http
def main(request):
    if request == 'db':
        request_args = db_request["args"]
        print("Debug mode")
    else:
        request_args = request.get_json(silent=True)
        if request_args is None:
            print("No json arguments detected")
            return HTTPStatus.BAD_REQUEST

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
    if (df_config.empty):
        print("No se encontró configuración para las notificaciones")
        return HTTPStatus.NO_CONTENT

    df_inv                  = bq.get_pending_invoices(invoice_table_id, bq_client)
    internal_notif_msgs     = utils.read_json_file(internal_notif_msgs_path)
    external_notif_msgs     = utils.read_json_file(external_notif_msgs_path)
    inv_notified_int        = []
    inv_notified_ext        = []

    if trig.send_receipt_notif(df_config):
        internal_receipt_mail = inb.build_internal_receipt_notif(internal_notif_msgs, df_config, df_inv, inv_notified_int, looker_config_link)
        smtp.send_email_smtp(internal_receipt_mail, smtp_sender, smtp_password)
        print("Receipt notification email sent")
    else:
        print("Receipt notification not configured")

    if trig.send_payement_notif(df_config):
        internal_payement_mail  = inb.build_internal_payements_notif(internal_notif_msgs, df_config, df_inv, inv_notified_int)
        smtp.send_email_smtp(internal_payement_mail, smtp_sender, smtp_password)
        print("Payement notification email sent")
    else:
        print("Payement notification not configured")

    if inv_notified_int:
        bq.update_notification_status_int(invoice_table_id, bq_client, inv_notified_int)
        print("Internal notification status has been updated in BQ")


    clients_to_notify = trig.get_clients_to_notify(df_config, df_inv)
    for client in clients_to_notify:
        external_mail = enb.build_external_notif(external_notif_msgs, df_config, df_inv, client, inv_notified_ext, company_name)
        smtp.send_email_smtp(external_mail, smtp_sender, smtp_password)
        print("External notification sent to ", client)

    if inv_notified_ext:
        bq.update_notification_status_ext(invoice_table_id, bq_client, inv_notified_ext)
        print("External notification status has been updated in BQ")

    print("Las notificaciones fueron enviadas!")
    return HTTPStatus.OK


# # ------------------------------------------------------------------------
# #   Trigger main function execution when this file is run
# # ------------------------------------------------------------------------
if __name__ == "__main__":
    main('db')
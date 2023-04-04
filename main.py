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
company_name                = "sandbox"
notif_table_id              = "fili-377220.fili_sandbox.bq_notification_config"
invoice_table_id            = "fili-377220.fili_sandbox.invoices"
looker_config_link          = 'https://lookerstudio.google.com/u/0/reporting/6d0fee52-f9c6-495c-b7a1-c778a83a29c0/page/p_hsqtmpj82c'
email_sender                = "anusmartin1@gmail.com"


# ------------------------------------------------------------------------
# function:
#   main()
# ------------------------------------------------------------------------
@functions_framework.http
def main(request):

    bq_client               = bq.get_client(key_path)
    df_config               = bq.get_configuration(notif_table_id, bq_client)
    df_inv                  = bq.get_pending_invoices(invoice_table_id, bq_client)
    internal_notif_msgs     = utils.read_json_file(internal_notif_msgs_path)
    external_notif_msgs     = utils.read_json_file(external_notif_msgs_path)
    inv_notified_int        = []
    inv_notified_ext        = []

    # if trig.trigger_receipt_notif(df_config, df_inv):
    #     internal_receipt_mail = inb.build_internal_receipt_notif(internal_notif_msgs, df_config, df_inv, inv_notified_int, looker_config_link)
    #     print(internal_receipt_mail["body"], '\n\n\n')
    #     smtp.send_email_smtp(internal_receipt_mail, email_sender)
    #     print("Receipt notification triggered")
    # else:
    #     print("Receipt notification not triggered")


    # if trig.trigger_payement_notif(df_config, df_inv):
    #     internal_payements_mail  = inb.build_internal_payements_notif(internal_notif_msgs, df_config, df_inv, inv_notified_int)
    #     print(internal_payements_mail["body"], '\n\n\n')
    #     smtp.send_email_smtp(internal_payements_mail, email_sender)
    #     print("Payement notification triggered")
    # else:
    #     print("Payement notification not triggered")

    # bq.update_notification_status_int(invoice_table_id, bq_client, inv_notified_int)
    # print("Notification status has been updated in BQ")


    clients_to_notify = trig.get_clients_to_notify(df_config, df_inv)
    for client in clients_to_notify:
        external_mail = enb.build_external_notif(external_notif_msgs, df_config, df_inv, client, inv_notified_ext, company_name)
        # smtp.send_email_smtp(external_mail, email_sender)
        print("\n \n External notification sent to ", client)
        print(external_mail['body'])



    return "Las notificaciones fueron enviadas!"


# ------------------------------------------------------------------------
#   Trigger main function execution when this file is run
# ------------------------------------------------------------------------
if __name__ == "__main__":
    main('')
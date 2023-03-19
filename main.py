# Library imports
import functions_framework
import requests

# File imports
import trigger_logic as trig
import notification_build as nb
import big_query as bq
import utils
import smtp


# ------------------------------------------------------------------------
# Global variables 
# ------------------------------------------------------------------------
key_path                = "credentials.json"
notif_msg_path          = "notif_msg.json"
notif_table_id          = "fili-377220.fili_demo.bq_notification_config"
invoice_table_id        = "fili-377220.fili_demo.fili_schedule"
email_sender            = "anusmartin1@gmail.com"

client                  = bq.get_client(key_path)
df_config               = bq.get_configuration(notif_table_id, client)
df_inv                  = bq.get_pending_invoices(invoice_table_id, client)
notif_msgs              = utils.read_json_file(notif_msg_path)
internal_email          = utils.get_mails_as_list(df_config)
inv_notified            = []


# ------------------------------------------------------------------------
# function: 
#   main(request)
# ------------------------------------------------------------------------
@functions_framework.http
def main(request):    

    if (trig.trigger_receipt_notif(df_config, df_inv)):
        internal_receipt_mail = nb.build_internal_receipt_notif(notif_msgs, df_config, df_inv, inv_notified)
        print(internal_receipt_mail["body"], '\n\n\n')        
        smtp.send_email_smtp(internal_receipt_mail, email_sender, internal_email)
        print("Receipt notification triggered")
    else:
        print("Receipt notification not triggered")

    
    if (trig.trigger_payement_notif(df_config, df_inv)):
        internal_payements_mail  = nb.build_internal_payements_notif(notif_msgs, df_config, df_inv, inv_notified)
        print(internal_payements_mail["body"], '\n\n\n')
        smtp.send_email_smtp(internal_payements_mail, email_sender, internal_email)
        print("Payement notification triggered")
    else:
        print("Payement notification not triggered")

    bq.update_notification_status(invoice_table_id, client, inv_notified)
    print("Notification status has been updated in BQ")
    
    #external_pre_notif      = utils.get_days_as_list(df_config, "external_pre_notif")
    #external_post_notif     = utils.get_days_as_list(df_config, "external_post_notif")
    #print("external_pre_notif:", external_pre_notif)
    #print("external_post_notif: " ,cexternal_post_notif)

    # trigger on mondays (don't forget dues on weekend)
    # adds payement configuration link to suggestions in mails

    return "Las notificaciones fueron enviadas!"


# ------------------------------------------------------------------------
#   Trigger main function execution when this file is run
# ------------------------------------------------------------------------
if __name__ == "__main__":
    main('')
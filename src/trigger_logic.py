import utils


# ------------------------------------------------------------------------
# function:
#   send_receipt_notif()
# ------------------------------------------------------------------------
def send_receipt_notif(df_config):
    notif_type = df_config["internal_notification_type"].values[0]

    if (notif_type == "Cobros") or (notif_type == "Ambos"):

        return True

    return False


# ------------------------------------------------------------------------
# function:
#   send_payement_notif()
# ------------------------------------------------------------------------
def send_payement_notif(df_config):
    notif_type = df_config["internal_notification_type"].values[0]

    if (notif_type == "Pagos") or (notif_type == "Ambos"):
        return True

    return False


# ------------------------------------------------------------------------
# function:
#   get_clients_to_notify()
# ------------------------------------------------------------------------
def get_clients_to_notify(df_config, df_inv):

    external_pre_notif_days      = utils.get_days_as_list(df_config, "external_pre_notif")
    external_post_notif_days     = utils.get_days_as_list(df_config, "external_post_notif", neg_list=True)
    external_notif_days          = external_pre_notif_days + external_post_notif_days

    df = df_inv[(df_inv.is_income==True) &
                (df_inv.days_to_pay.isin(external_notif_days)) &
                (df_inv.notification_status_ext!='exclude')]

    clients = df['counterpart'].unique()

    return clients
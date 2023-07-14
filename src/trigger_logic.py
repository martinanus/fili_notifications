import utils


# ------------------------------------------------------------------------
# function:
#   send_receipt_notif()
# ------------------------------------------------------------------------
def send_receipt_notif(df_config):
    notif_type = df_config["internal_notification_type"].values[0]

    if (notif_type == "Cobros") or (notif_type == "Ambos"):
        if utils.is_monday() is True:
            return True

    return False


# ------------------------------------------------------------------------
# function:
#   send_payement_notif()
# ------------------------------------------------------------------------
def send_payement_notif(df_config):
    notif_type = df_config["internal_notification_type"].values[0]

    if (notif_type == "Pagos") or (notif_type == "Ambos"):
        if utils.is_monday() is True:
            return True

    return False


# ------------------------------------------------------------------------
# function:
#   get_clients_to_notify()
# ------------------------------------------------------------------------
def get_clients_to_notify(df_inv):

    df_inc              = utils.get_df_income(df_inv)
    df_due_inc          = utils.get_due_invoices(df_inc)

    limit_days          = utils.days_left_in_week()
    df_upcoming_inc     = utils.get_upcoming_invoices(df_inc, limit_days)


    df      = df_due_inc.append(df_upcoming_inc)

    clients = df['counterpart'].unique()

    return clients
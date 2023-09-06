import utils

# ------------------------------------------------------------------------
# function:
#   send_daily_due_notification()
# ------------------------------------------------------------------------
def send_daily_due_notification(df_config, df_inv):
    # TODO - read this configuration from BQ
    #enable = df_config["daily_due_notification_enable"].values[0]
    enable = True

    if enable:
        df_today_due_inv = utils.get_today_due_invoices(df_inv)
        if not df_today_due_inv.empty:
            return True

    return False

# ------------------------------------------------------------------------
# function:
#   send_internal_receipt_notif()
# ------------------------------------------------------------------------
def send_internal_receipt_notif(df_config):
    notif_type = df_config["internal_notification_type"].values[0]

    if (notif_type == "Cobros") or (notif_type == "Ambos"):
        if utils.is_monday():
            return True

    return False


# ------------------------------------------------------------------------
# function:
#   send_internal_payement_notif()
# ------------------------------------------------------------------------
def send_internal_payement_notif(df_config):
    notif_type = df_config["internal_notification_type"].values[0]

    if (notif_type == "Pagos") or (notif_type == "Ambos"):
        if utils.is_monday():
            return True

    return False


# ------------------------------------------------------------------------
# function:
#   send_external_notif()
# ------------------------------------------------------------------------
def send_external_notif(df_config):
    enable = df_config["external_notif_enable"].values[0]

    if enable:
        if (utils.is_monday()) or (utils.is_thursday()):
            return True

    return False
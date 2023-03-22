import utils

# ------------------------------------------------------------------------
# function: 
#   trigger_receipt_notif()
# ------------------------------------------------------------------------
def trigger_receipt_notif(df_config, df_inv):
    
    if utils.is_monday():
        return True
    
    internal_pre_notif_days      = utils.get_days_as_list(df_config, "internal_pre_notif_collect")
    internal_post_notif_days     = utils.get_days_as_list(df_config, "internal_post_notif_collect", neg_list=True)
    internal_notif_days          = internal_pre_notif_days + internal_post_notif_days
    
    df = df_inv[(df_inv.relation=='Cliente') & (df_inv.days_to_pay.isin(internal_notif_days))]
    
    return df.size 

# ------------------------------------------------------------------------
# function: 
#   trigger_payement_notif()
# ------------------------------------------------------------------------
def trigger_payement_notif(df_config, df_inv):
    
    if utils.is_monday():
        return True
    
    internal_pre_notif_days      = utils.get_days_as_list(df_config, "internal_pre_notif_pay")
    internal_post_notif_days     = utils.get_days_as_list(df_config, "internal_post_notif_pay", neg_list=True)
    
    internal_notif_days         = internal_pre_notif_days + internal_post_notif_days
    
    df = df_inv[(df_inv.relation=='Proveedor') & (df_inv.days_to_pay.isin(internal_notif_days))]
    
    return df.size     

from .ld_client import ld_client

def is_enabled(flag_key, context, default=False):
    return ld_client.variation(flag_key, context, default)

import ldclient
from ldclient.config import Config
from django.conf import settings
from ldobserve import ObservabilityPlugin
from decouple import config

sdk_key = str(config('LAUNCHDARKLY_SDK_KEY', cast=str, default=''))
ldclient.set_config(ldclient.Config(sdk_key, plugins=[ObservabilityPlugin()]))

def ld_client():
    return ldclient.get()

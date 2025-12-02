from ldclient.client import LDClient  
from django.conf import settings

ld_client = LDClient(settings.LAUNCHDARKLY_SDK_KEY)

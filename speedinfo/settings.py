# coding: utf-8

from django.conf import settings

SPEEDINFO_CACHED_RESPONSE_ATTR_NAME = getattr(settings, 'SPEEDINFO_CACHED_RESPONSE_ATTR_NAME', 'is_cached')
SPEEDINFO_EXCLUDE_URLS = getattr(settings, 'SPEEDINFO_EXCLUDE_URLS', [])

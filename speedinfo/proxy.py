# coding: utf-8

from django.core.cache import CacheHandler
from speedinfo.settings import SPEEDINFO_CACHED_RESPONSE_ATTR_NAME


class ProfilerCacheProxy(object):
    """
    Proxy access to cache instance to intercept requests to cached pages
    when using default Django per-site middleware or per-view cache decorator.
    """
    def __init__(self, instance):
        object.__setattr__(self, '_instance', instance)

    def get(self, key, default=None, version=None):
        response = self._instance.get(key, default, version)

        # Sets the flag for marking response from cache
        if (response is not None) and key.startswith('views.decorators.cache.cache_page'):
            setattr(response, SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, True)

        return response

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __setattr__(self, name, value):
        return setattr(self._instance, name, value)

    def __delattr__(self, name):
        return delattr(self._instance, name)

    def __contains__(self, key):
        return key in self._instance

    def __eq__(self, other):
        return self._instance == other

    def __ne__(self, other):
        return self._instance != other


class ProfilerCacheHandler(CacheHandler):
    def __getitem__(self, alias):
        return ProfilerCacheProxy(
            super(ProfilerCacheHandler, self).__getitem__(alias)
        )

# coding: utf-8

from django.core.cache import InvalidCacheBackendError
from django.utils.module_loading import import_string

from speedinfo.settings import speedinfo_settings


def proxy_cache(location, params):
    backend = params.pop('CACHE_BACKEND')

    try:
        backend_cls = import_string(backend)
    except ImportError as e:
        raise InvalidCacheBackendError('Could not find backend "{}": {}'.format(backend, e))

    class ProxyCacheBackend(backend_cls):
        """
        Proxy access to cache backend to intercept requests to cached pages
        when using default Django per-site middleware or per-view cache decorator.
        """
        def get(self, key, default=None, version=None):
            response = super(ProxyCacheBackend, self).get(key, default, version)

            # Sets the flag for marking response from cache
            if (response is not None) and key.startswith('views.decorators.cache.cache_page'):
                setattr(response, speedinfo_settings.SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, True)

            return response

    return ProxyCacheBackend(location, params)

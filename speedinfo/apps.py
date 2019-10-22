# coding: utf-8

import django
from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, Warning, register

from speedinfo.utils import import_class

if django.VERSION < (1, 10):
    MIDDLEWARE_SETTINGS_NAME = "MIDDLEWARE_CLASSES"
else:
    MIDDLEWARE_SETTINGS_NAME = "MIDDLEWARE"


def check_middleware(app_configs, **kwargs):
    profiler_middleware_index = None
    profiler_middleware_multiple = False
    cache_middleware_index = None
    errors = []

    for i, middleware in enumerate(getattr(settings, MIDDLEWARE_SETTINGS_NAME)):
        if middleware == "speedinfo.middleware.ProfilerMiddleware":
            profiler_middleware_multiple = profiler_middleware_index is not None
            profiler_middleware_index = i
        elif middleware == "django.middleware.cache.FetchFromCacheMiddleware":
            cache_middleware_index = i

    if profiler_middleware_index is None:
        errors.append(
            Warning(
                "speedinfo.middleware.ProfilerMiddleware is missing from %s" % MIDDLEWARE_SETTINGS_NAME,
                hint="Add speedinfo.middleware.ProfilerMiddleware to %s" % MIDDLEWARE_SETTINGS_NAME,
                id="speedinfo.W001",
            ),
        )

    elif (cache_middleware_index is not None) and (profiler_middleware_index > cache_middleware_index):
        errors.append(
            Error(
                "speedinfo.middleware.ProfilerMiddleware occurs after "
                "django.middleware.cache.FetchFromCacheMiddleware in %s" % MIDDLEWARE_SETTINGS_NAME,
                hint="Move speedinfo.middleware.ProfilerMiddleware to before "
                     "django.middleware.cache.FetchFromCacheMiddleware in %s" % MIDDLEWARE_SETTINGS_NAME,
                id="speedinfo.E001",
            ),
        )

    elif profiler_middleware_multiple:
        errors.append(
            Error(
                "speedinfo.middleware.ProfilerMiddleware occurs multiple times in %s" % MIDDLEWARE_SETTINGS_NAME,
                hint="Add speedinfo.middleware.ProfilerMiddleware only once in %s" % MIDDLEWARE_SETTINGS_NAME,
                id="speedinfo.E002",
            ),
        )

    return errors


def check_cache_backend(app_configs, **kwargs):
    for params in settings.CACHES.values():
        if params.get("BACKEND") == "speedinfo.backends.proxy_cache":
            return []

    return [
        Error(
            "speedinfo.backends.proxy_cache is missing from CACHES",
            hint="Add speedinfo.backends.proxy_cache to CACHES",
            id="speedinfo.E003",
        ),
    ]


def check_storage(app_configs, **kwargs):
    if not getattr(settings, "SPEEDINFO_STORAGE", None):
        return [
            Error(
                "SPEEDINFO_STORAGE is None or missing from the settings",
                hint="Assign a dotted module path to one of available storage classes to the SPEEDINFO_STORAGE",
                id="speedinfo.E004",
            ),
        ]

    try:
        import_class(settings.SPEEDINFO_STORAGE)
    except ImportError:
        return [
            Error(
                "Could not import class by path in SPEEDINFO_STORAGE",
                hint="Ensure that module and class at specified path is importable",
                id="speedinfo.E005",
            ),
        ]
    else:
        return []


class SpeedinfoConfig(AppConfig):
    name = "speedinfo"

    def ready(self):
        register()(check_middleware)
        register()(check_cache_backend)
        register()(check_storage)

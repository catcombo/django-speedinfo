# coding: utf-8

from django.conf import settings

DEFAULTS = {
    "SPEEDINFO_TESTS": False,
    "SPEEDINFO_CACHED_RESPONSE_ATTR_NAME": "is_cached",
    "SPEEDINFO_STORAGE": None,
    "SPEEDINFO_CACHE_STORAGE_CACHE_ALIAS": "default",
    "SPEEDINFO_PROFILING_CONDITIONS": [],
    "SPEEDINFO_EXCLUDE_URLS": [],
    "SPEEDINFO_ADMIN_COLUMNS": (
        ("View name", "{}", "view_name"),
        ("HTTP method", "{}", "method"),
        ("Anonymous calls", "{:.1f}%", "anon_calls_ratio"),
        ("Cache hits", "{:.1f}%", "cache_hits_ratio"),
        ("SQL queries per call", "{}", "sql_count_per_call"),
        ("SQL time", "{:.1f}%", "sql_time_ratio"),
        ("Total calls", "{}", "total_calls"),
        ("Time per call", "{:.8f}", "time_per_call"),
        ("Total time", "{:.4f}", "total_time"),
    ),
}


class SpeedinfoSettings:
    def __init__(self, defaults=None):
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, name):
        if name not in self.defaults:
            raise AttributeError("Invalid setting: '{}'".format(name))

        return getattr(settings, name, self.defaults.get(name))


speedinfo_settings = SpeedinfoSettings()

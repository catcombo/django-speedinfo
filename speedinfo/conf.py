# coding: utf-8

from collections import namedtuple

from django.conf import settings

ReportColumnFormat = namedtuple("ReportColumnFormat", ["name", "format", "attr_name"])

DEFAULTS = {
    "SPEEDINFO_TESTS": False,
    "SPEEDINFO_CACHED_RESPONSE_ATTR_NAME": "is_cached",
    "SPEEDINFO_STORAGE": None,
    "SPEEDINFO_CACHE_STORAGE_CACHE_ALIAS": "default",
    "SPEEDINFO_PROFILING_CONDITIONS": [],
    "SPEEDINFO_EXCLUDE_URLS": [],
    "SPEEDINFO_REPORT_COLUMNS": (
        "view_name", "method", "anon_calls_ratio", "cache_hits_ratio",
        "sql_count_per_call", "sql_time_ratio", "total_calls", "time_per_call", "total_time",
    ),
    "SPEEDINFO_REPORT_COLUMNS_FORMAT": [
        ReportColumnFormat("View name", "{}", "view_name"),
        ReportColumnFormat("HTTP method", "{}", "method"),
        ReportColumnFormat("Anonymous calls", "{:.1f}%", "anon_calls_ratio"),
        ReportColumnFormat("Cache hits", "{:.1f}%", "cache_hits_ratio"),
        ReportColumnFormat("SQL queries per call", "{}", "sql_count_per_call"),
        ReportColumnFormat("SQL time", "{:.1f}%", "sql_time_ratio"),
        ReportColumnFormat("Total calls", "{}", "total_calls"),
        ReportColumnFormat("Time per call", "{:.8f}", "time_per_call"),
        ReportColumnFormat("Total time", "{:.4f}", "total_time"),
    ],
}


class SpeedinfoSettings:
    def __init__(self, defaults=None):
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, name):
        if name not in self.defaults:
            raise AttributeError("Invalid setting: '{}'".format(name))

        return getattr(settings, name, self.defaults.get(name))


speedinfo_settings = SpeedinfoSettings()

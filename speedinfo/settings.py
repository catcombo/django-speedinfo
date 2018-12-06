# coding: utf-8

from collections import namedtuple
from django.conf import settings
from django.db.models import ExpressionWrapper, F, FloatField, IntegerField

SPEEDINFO_CACHED_RESPONSE_ATTR_NAME = getattr(settings, 'SPEEDINFO_CACHED_RESPONSE_ATTR_NAME', 'is_cached')
SPEEDINFO_EXCLUDE_URLS = getattr(settings, 'SPEEDINFO_EXCLUDE_URLS', [])
SPEEDINFO_REPORT_COLUMNS = getattr(settings, 'SPEEDINFO_REPORT_COLUMNS', (
    'view_name', 'method', 'anon_calls_ratio', 'cache_hits_ratio',
    'sql_count_per_call', 'sql_time_ratio', 'total_calls', 'time_per_call', 'total_time'))

ReportColumnFormat = namedtuple('ReportColumnFormat', ['name', 'format', 'attr_name', 'order_field'])
SPEEDINFO_REPORT_COLUMNS_FORMAT = [
    ReportColumnFormat('View name', '{}', 'view_name', 'view_name'),
    ReportColumnFormat('HTTP method', '{}', 'method', 'method'),
    ReportColumnFormat('Anonymous calls', '{:.1f}%', 'anon_calls_ratio',
                       ExpressionWrapper(100.0 * F('anon_calls') / F('total_calls'), output_field=FloatField())),
    ReportColumnFormat('Cache hits', '{:.1f}%', 'cache_hits_ratio',
                       ExpressionWrapper(100.0 * F('cache_hits') / F('total_calls'), output_field=FloatField())),
    ReportColumnFormat('SQL queries per call', '{}', 'sql_count_per_call',
                       ExpressionWrapper(F('sql_total_count') / F('total_calls'), output_field=IntegerField())),
    ReportColumnFormat('SQL time', '{:.1f}%', 'sql_time_ratio',
                       ExpressionWrapper(100.0 * F('sql_total_time') / F('total_time'), output_field=FloatField())),
    ReportColumnFormat('Total calls', '{}', 'total_calls', 'total_calls'),
    ReportColumnFormat('Time per call', '{:.8f}', 'time_per_call',
                       ExpressionWrapper(F('total_time') / F('total_calls'), output_field=FloatField())),
    ReportColumnFormat('Total time', '{:.4f}', 'total_time', 'total_time'),
]

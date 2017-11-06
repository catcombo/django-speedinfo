# coding: utf-8

import csv

from StringIO import StringIO
from django.core.cache import cache
from django.db import IntegrityError

from speedinfo import settings


class Profiler(object):
    """
    Profiler class to save it's state and process the data.
    """
    PROFILER_STATE_CACHE_KEY = 'speedinfo.profiler.is_on'

    @property
    def is_on(self):
        """Returns state of the profiler.

        :return: state of the profiler
        :rtype: bool
        """
        return cache.get(self.PROFILER_STATE_CACHE_KEY, False)

    @is_on.setter
    def is_on(self, value):
        """Sets state of the profiler.

        :param bool value: State value
        """
        cache.set(self.PROFILER_STATE_CACHE_KEY, value, None)

    def switch(self):
        """Toggles state of the profiler"""
        self.is_on = not self.is_on

    def process(self, view_name, method, is_anon_call, is_cache_hit, sql_time, sql_count, duration):
        """Saves request data and statistics.

        :param str view_name: View name
        :param str method: HTTP method (GET, POST, etc.)
        :param bool is_anon_call: If True, it was an anonymous request
        :param bool is_cache_hit: If True, view response was retrieved from cache
        :param float sql_time: SQL queries execution time
        :param int sql_count: Number of SQL queries
        :param float duration: Duration of the view response
        """
        from django.db.models import F
        from speedinfo.models import ViewProfiler

        try:
            vp, created = ViewProfiler.objects.get_or_create(view_name=view_name, method=method)
        except IntegrityError:
            # IntegrityError exception raised in case of concurrent access
            # to get_or_create method from another webserver worker process
            vp = ViewProfiler.objects.get(view_name=view_name, method=method)

        ViewProfiler.objects.filter(pk=vp.pk).update(
            anon_calls=F('anon_calls') + (is_anon_call and 1 or 0),
            cache_hits=F('cache_hits') + (is_cache_hit and 1 or 0),
            sql_total_time=F('sql_total_time') + sql_time,
            sql_total_count=F('sql_total_count') + sql_count,
            total_calls=F('total_calls') + 1,
            total_time=F('total_time') + duration
        )

    def export(self):
        """Exports profiling data as a comma-separated file-like object.

        :return: comma-separated profiling data
        :rtype: :class:`StringIO`
        """
        from speedinfo.models import ViewProfiler

        output = StringIO()
        export_columns = filter(lambda col: col.attr_name in settings.SPEEDINFO_REPORT_COLUMNS,
                                settings.SPEEDINFO_REPORT_COLUMNS_FORMAT)

        csv_writer = csv.writer(output)
        csv_writer.writerow([col.name for col in export_columns])

        for vp in ViewProfiler.objects.order_by('-total_time'):
            csv_writer.writerow([
                col.format.format(getattr(vp, col.attr_name))
                for col in export_columns
            ])

        return output

    def flush(self):
        """Deletes all profiling data"""
        from speedinfo.models import ViewProfiler
        ViewProfiler.objects.all().delete()

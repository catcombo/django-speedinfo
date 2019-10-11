# coding: utf-8

from django.db import IntegrityError, models
from django.db.models import F


class ViewProfilerManager(models.Manager):
    def add(self, view_name, method, is_anon_call, is_cache_hit, sql_time, sql_count, view_execution_time):
        """Adds profiling data.

        :param str view_name: View name
        :param str method: HTTP method (GET, POST, etc.)
        :param bool is_anon_call: If True, it was an anonymous request
        :param bool is_cache_hit: If True, view response was retrieved from cache
        :param float sql_time: SQL queries execution time
        :param int sql_count: Number of SQL queries
        :param float view_execution_time: View execution time
        """

        try:
            vp, created = self.get_queryset().get_or_create(view_name=view_name, method=method)
        except IntegrityError:
            # IntegrityError raised in the case of concurrent access
            # to get_or_create method from another application worker/thread
            vp = self.get_queryset().get(view_name=view_name, method=method)

        self.get_queryset().filter(pk=vp.pk).update(
            anon_calls=F("anon_calls") + (is_anon_call and 1 or 0),
            cache_hits=F("cache_hits") + (is_cache_hit and 1 or 0),
            sql_total_time=F("sql_total_time") + sql_time,
            sql_total_count=F("sql_total_count") + sql_count,
            total_calls=F("total_calls") + 1,
            total_time=F("total_time") + view_execution_time,
        )

    def reset(self):
        """Deletes all profiling data"""
        self.get_queryset().all().delete()

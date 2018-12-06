# coding: utf-8

from django.db import models


class ViewProfiler(models.Model):
    """
    Holds profiler stats grouped by view.
    """
    view_name = models.CharField('View name', max_length=255)
    method = models.CharField('HTTP method', max_length=8)
    anon_calls = models.PositiveIntegerField('Anonymous calls', default=0)
    cache_hits = models.PositiveIntegerField('Cache hits', default=0)
    sql_total_time = models.FloatField('SQL total time', default=0)
    sql_total_count = models.PositiveIntegerField('SQL total queries count', default=0)
    total_calls = models.PositiveIntegerField('Total calls', default=0)
    total_time = models.FloatField('Total time', default=0)

    class Meta:
        verbose_name_plural = 'Views'
        unique_together = ('view_name', 'method')

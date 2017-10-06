# coding: utf-8

from django.db import models


class ViewProfiler(models.Model):
    view_name = models.CharField('View name', max_length=255)
    method = models.CharField('HTTP method', max_length=8)
    anon_calls = models.PositiveIntegerField('Anonymous calls', default=0)
    cache_hits = models.PositiveIntegerField('Cache hits', default=0)
    total_calls = models.PositiveIntegerField('Total calls', default=0)
    total_time = models.FloatField('Total time', default=0)

    class Meta:
        verbose_name_plural = 'Views profiler'

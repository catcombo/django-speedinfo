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
    total_calls = models.PositiveIntegerField('Total calls', default=0)
    total_time = models.FloatField('Total time', default=0)

    class Meta:
        verbose_name_plural = 'Views profiler'

    @property
    def anon_calls_ratio(self):
        """Anonymous calls ratio.

        :return: anonymous calls ratio percent
        :rtype: float
        """
        return 100 * self.anon_calls / float(self.total_calls)

    @property
    def cache_hits_ratio(self):
        """Cache hits ratio.

        :return: cache hits ratio percent
        :rtype: float
        """
        return 100 * self.cache_hits / float(self.total_calls)

    @property
    def time_per_call(self):
        """Time per call.

        :return: time per call
        :rtype: float
        """
        return self.total_time / float(self.total_calls)

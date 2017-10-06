# coding: utf-8

from django.core.cache import cache


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

    def process(self, view_name, method, is_anon_call, is_cache_hit, duration):
        """Saves request data and statistics.

        :param str view_name: View name
        :param str method: HTTP method (GET, POST, etc.)
        :param bool is_anon_call: If True, it was an anonymous request
        :param bool is_cache_hit: If True, view response was retrieved from cache
        :param float duration: Duration of the view response
        """
        from django.db.models import F
        from speedinfo.models import ViewProfiler

        vp, created = ViewProfiler.objects.get_or_create(
            view_name=view_name,
            method=method
        )

        ViewProfiler.objects.filter(pk=vp.pk).update(
            anon_calls=F('anon_calls') + (is_anon_call and 1 or 0),
            cache_hits=F('cache_hits') + (is_cache_hit and 1 or 0),
            total_calls=F('total_calls') + 1,
            total_time=F('total_time') + duration
        )

    def flush(self):
        """Deletes all profiling data"""
        from speedinfo.models import ViewProfiler
        ViewProfiler.objects.all().delete()

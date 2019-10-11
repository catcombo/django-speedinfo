# coding: utf-8

from django.core.cache import cache


class Profiler(object):
    """
    Profiler class to store its state and process the data.
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

    def add(self, *args, **kwargs):
        from speedinfo.models import ViewProfiler
        ViewProfiler.objects.add(*args, **kwargs)

    def reset(self):
        from speedinfo.models import ViewProfiler
        ViewProfiler.objects.reset()

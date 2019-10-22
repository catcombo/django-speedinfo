# coding: utf-8

from django.core.cache import cache

from speedinfo.conf import speedinfo_settings
from speedinfo.utils import import_class


class Profiler(object):
    """
    Used to store profiler state and storage.
    """
    PROFILER_STATE_CACHE_KEY = "speedinfo.profiler.is_on"

    def __init__(self):
        self._storage = None

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

    @property
    def storage(self):
        """Returns profiler storage.

        :return: storage instance
        :rtype: :class:`speedinfo.storage.base.AbstractStorage`
        """
        if self._storage is None:
            self._storage = import_class(speedinfo_settings.SPEEDINFO_STORAGE)()

        return self._storage

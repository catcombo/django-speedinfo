# coding: utf-8

from abc import ABCMeta, abstractmethod


class AbstractStorage(object):
    """
    Base class for user-defined storage implementations.
    Storage is used to save and manipulate profiling data.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def add(self, view_name, method, is_anon_call, is_cache_hit, sql_time, sql_count, view_execution_time):
        """Adds a new entry.

        :param str view_name: View name
        :param str method: HTTP method (GET, POST, etc.)
        :param bool is_anon_call: True in case of an anonymous request
        :param bool is_cache_hit: True if view response was retrieved from cache
        :param float sql_time: SQL queries execution time
        :param int sql_count: Number of executed SQL queries
        :param float view_execution_time: View execution time
        :rtype: None
        """

    @abstractmethod
    def fetch_all(self, ordering=None):
        """Returns all entries optionally sorted by specified list of fields.

        :param ordering: list of field names to sort the entries (e.g. ['-sql_total_time', 'total_calls'])
        :type ordering: list[str] or None
        :rtype: list of :class:`speedinfo.models.ViewProfiler`
        """

    @abstractmethod
    def reset(self):
        """Deletes all entries.

        :rtype: None
        """

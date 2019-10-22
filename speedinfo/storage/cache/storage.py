# coding: utf-8

from functools import cmp_to_key

from django.core.cache import caches

from speedinfo.conf import speedinfo_settings
from speedinfo.models import ViewProfiler
from speedinfo.storage.base import AbstractStorage


def comparator(order_fields):
    """Returns a function to be used as a comparator
    in build-in `sorted` function to sort list of objects.

    :param order_fields: list of pairs (attribute name, flag of descending sort order)
    :type order_fields: list[tuple(str, bool)]
    :return: comparator function
    """
    def compare(a, b):
        for field_name, desc_order in order_fields:
            if getattr(a, field_name) == getattr(b, field_name):
                continue
            elif getattr(a, field_name) > getattr(b, field_name):
                return -1 if desc_order else 1
            else:
                return 1 if desc_order else -1
        return 0
    return compare


class CacheStorage(AbstractStorage):
    """
    Storage implementation for data stored in the cache.
    Use SPEEDINFO_CACHE_STORAGE_CACHE_ALIAS to specify
    cache alias if different from `default`.
    """
    CACHE_KEY_PREFIX = "speedinfo"
    CACHE_INDEXES_KEY = "speedinfo:indexes"

    def __init__(self):
        self._cache = caches[speedinfo_settings.SPEEDINFO_CACHE_STORAGE_CACHE_ALIAS]

    def get_cache_key(self, *args):
        return ".".join([self.CACHE_KEY_PREFIX] + list(args))

    def indexes(self):
        val = self._cache.get(self.CACHE_INDEXES_KEY)

        if val is None:
            self._cache.add(self.CACHE_INDEXES_KEY, [], None)
            val = self._cache.get(self.CACHE_INDEXES_KEY)

        return val

    def add_index(self, name):
        self._cache.set(self.CACHE_INDEXES_KEY, list(set(self.indexes() + [name])), None)

    def add(self, view_name, method, is_anon_call, is_cache_hit, sql_time, sql_count, view_execution_time):
        index = self.get_cache_key(view_name, method)
        entry = self._cache.get(index)

        if entry is None:
            entry = {
                "view_name": view_name,
                "method": method,
                "anon_calls": 0,
                "cache_hits": 0,
                "sql_total_time": 0,
                "sql_total_count": 0,
                "total_calls": 0,
                "total_time": 0,
            }
            self._cache.set(index, entry, None)
            self.add_index(index)

        entry["anon_calls"] += is_anon_call and 1 or 0
        entry["cache_hits"] += is_cache_hit and 1 or 0
        entry["sql_total_time"] += sql_time
        entry["sql_total_count"] += sql_count
        entry["total_calls"] += 1
        entry["total_time"] += view_execution_time

        self._cache.set(index, entry, None)

    def fetch_all(self, ordering=None):
        results = [
            ViewProfiler(**self._cache.get(index))
            for index in self.indexes()
        ]

        order_fields = [
            (field[1:], True) if field.startswith("-") else (field, False)
            for field in ordering or []
        ]

        return sorted(results, key=cmp_to_key(comparator(order_fields)))

    def reset(self):
        self._cache.delete_many(self.indexes() + [self.CACHE_INDEXES_KEY])

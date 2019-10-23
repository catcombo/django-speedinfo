# coding: utf-8

from django.forms import model_to_dict
from django.test import TestCase, override_settings

from speedinfo.conf import speedinfo_settings
from speedinfo.models import ViewProfiler
from speedinfo.utils import import_class


class StorageTestCase(object):
    @classmethod
    def setUpClass(cls):
        super(StorageTestCase, cls).setUpClass()
        cls.storage = import_class(speedinfo_settings.SPEEDINFO_STORAGE)()

    def setUp(self):
        self.storage.reset()

    def test_add(self):
        self.storage.add(
            view_name="app.view_name", method="GET", is_anon_call=True, is_cache_hit=True,
            sql_time=2, sql_count=3, view_execution_time=4,
        )
        entries = self.storage.fetch_all()

        self.assertEqual(len(entries), 1)
        self.assertDictEqual(dict(
            view_name="app.view_name", method="GET", anon_calls=1, cache_hits=1,
            sql_total_time=2, sql_total_count=3, total_calls=1, total_time=4,
        ), model_to_dict(entries[0], exclude=["id"]))

    def test_add_grouping(self):
        self.storage.add(
            view_name="app.view_name", method="GET", is_anon_call=True, is_cache_hit=False,
            sql_time=3, sql_count=2, view_execution_time=3,
        )
        self.storage.add(
            view_name="app.view_name", method="POST", is_anon_call=False, is_cache_hit=False,
            sql_time=10, sql_count=5, view_execution_time=7,
        )
        self.storage.add(
            view_name="app.view_name", method="GET", is_anon_call=True, is_cache_hit=True,
            sql_time=1, sql_count=1, view_execution_time=2,
        )

        entries = self.storage.fetch_all()
        dict_entries = [model_to_dict(e, exclude=["id"]) for e in entries]

        self.assertEqual(len(entries), 2)
        self.assertIn(dict(
            view_name="app.view_name", method="GET", anon_calls=2, cache_hits=1,
            sql_total_time=4, sql_total_count=3, total_calls=2, total_time=5,
        ), dict_entries)
        self.assertIn(dict(
            view_name="app.view_name", method="POST", anon_calls=0, cache_hits=0,
            sql_total_time=10, sql_total_count=5, total_calls=1, total_time=7,
        ), dict_entries)

    def test_entry_type(self):
        self.storage.add(
            view_name="app.view_name", method="GET", is_anon_call=True, is_cache_hit=False,
            sql_time=3, sql_count=2, view_execution_time=3,
        )
        entries = self.storage.fetch_all()
        self.assertIsInstance(entries, list)
        self.assertIsInstance(entries[0], ViewProfiler)

    def test_ordering(self):
        self.storage.add(
            view_name="view1", method="GET", is_anon_call=True, is_cache_hit=False,
            sql_time=3, sql_count=2, view_execution_time=3,
        )
        self.storage.add(
            view_name="view2", method="POST", is_anon_call=False, is_cache_hit=True,
            sql_time=10, sql_count=5, view_execution_time=7,
        )
        self.storage.add(
            view_name="view3", method="GET", is_anon_call=True, is_cache_hit=False,
            sql_time=4, sql_count=5, view_execution_time=10,
        )

        entries = self.storage.fetch_all(ordering=["-total_time"])
        self.assertEqual(entries[0].view_name, "view3")

        entries = self.storage.fetch_all(ordering=["sql_count_per_call"])
        self.assertEqual(entries[0].view_name, "view1")

        entries = self.storage.fetch_all(ordering=[
            "-sql_count_per_call", "total_time", "view_name", "method", "anon_calls", "cache_hits",
            "sql_total_time", "sql_total_count", "total_calls", "anon_calls_ratio", "cache_hits_ratio",
            "sql_time_ratio", "time_per_call",
        ])
        self.assertEqual(entries[0].view_name, "view2")

    def test_reset(self):
        self.storage.add(
            view_name="app.view_name", method="GET", is_anon_call=True, is_cache_hit=False,
            sql_time=3, sql_count=2, view_execution_time=3,
        )
        self.storage.reset()

        entries = self.storage.fetch_all()
        self.assertEqual(len(entries), 0)


@override_settings(
    SPEEDINFO_STORAGE="speedinfo.storage.cache.storage.CacheStorage",
    SPEEDINFO_CACHE_STORAGE_CACHE_ALIAS="custom",
    SPEEDINFO_TESTS=True,
    CACHES={
        "default": {
            "BACKEND": "speedinfo.backends.proxy_cache",
            "CACHE_BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
        "custom": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    })
class CacheStorageTestCase(StorageTestCase, TestCase):
    pass


@override_settings(SPEEDINFO_STORAGE="speedinfo.storage.database.storage.DatabaseStorage", SPEEDINFO_TESTS=True)
class DatabaseStorageTestCase(StorageTestCase, TestCase):
    pass

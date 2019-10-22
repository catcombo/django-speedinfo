# coding: utf-8

from django.core.cache import cache
from django.test import TestCase, override_settings

from speedinfo import profiler
from speedinfo.storage.cache.storage import CacheStorage


@override_settings(
    SPEEDINFO_STORAGE="speedinfo.storage.cache.storage.CacheStorage",
    SPEEDINFO_TESTS=True,
)
class ProfilerTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_state(self):
        self.assertFalse(profiler.is_on)
        profiler.is_on = True
        self.assertTrue(profiler.is_on)
        profiler.is_on = False
        self.assertFalse(profiler.is_on)

    def test_storage(self):
        self.assertIsInstance(profiler.storage, CacheStorage)

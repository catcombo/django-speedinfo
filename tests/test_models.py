# coding: utf-8

import mock
from django.test import TestCase, override_settings

from speedinfo.models import ViewProfiler


@override_settings(
    SPEEDINFO_STORAGE="speedinfo.storage.cache.storage.CacheStorage",
    SPEEDINFO_TESTS=True,
)
class ModelTestCase(TestCase):
    @mock.patch("speedinfo.managers.profiler")
    def test_fetch_all(self, profiler_mock):
        results = [mock.Mock(spec=ViewProfiler), mock.Mock(spec=ViewProfiler)]
        profiler_mock.storage.fetch_all.return_value = results

        self.assertListEqual(list(ViewProfiler.objects.all()), results)
        self.assertListEqual(list(ViewProfiler.objects.order_by("-total_time")), results)

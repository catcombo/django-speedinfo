# coding: utf-8

import mock
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from speedinfo.models import ViewProfiler

try:
    from django.urls import reverse  # Django >= 1.10
except ImportError:
    from django.core.urlresolvers import reverse


@override_settings(
    SPEEDINFO_STORAGE="speedinfo.storage.cache.storage.CacheStorage",
    SPEEDINFO_TESTS=True,
)
class ViewProfilerAdminTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ViewProfilerAdminTestCase, cls).setUpClass()
        User.objects.create_superuser(username="admin", email="", password="123456")

    def setUp(self):
        self.client.login(username="admin", password="123456")

    @mock.patch("speedinfo.admin.profiler")
    def test_switch(self, profiler_mock):
        profiler_mock.is_on = False
        self.client.get(reverse("admin:speedinfo-profiler-switch"))
        self.assertTrue(profiler_mock.is_on)

    @mock.patch("speedinfo.admin.profiler")
    def test_reset(self, profiler_mock):
        self.client.get(reverse("admin:speedinfo-profiler-reset"))
        profiler_mock.storage.reset.assert_called_once()

    @mock.patch("speedinfo.managers.profiler")
    def test_export(self, profiler_mock):
        profiler_mock.storage.fetch_all.return_value = [
            ViewProfiler(
                view_name="app.view_name", method="GET", anon_calls=8, cache_hits=3,
                sql_total_time=40, sql_total_count=20, total_calls=10, total_time=50,
            ),
        ]
        response = self.client.get(reverse("admin:speedinfo-profiler-export"))
        self.assertEquals(response.get("Content-Disposition"), "attachment; filename=profiler.csv")

        output = response.content.decode()
        self.assertEqual(
            output,
            "View name,HTTP method,Anonymous calls,Cache hits,SQL queries per call,"
            "SQL time,Total calls,Time per call,Total time\r\n"
            "app.view_name,GET,80.0%,30.0%,2,80.0%,10,5.00000000,50.0000\r\n",
        )

    @override_settings(SPEEDINFO_REPORT_COLUMNS=("view_name", "method", "total_calls", "time_per_call", "total_time"))
    @mock.patch("speedinfo.managers.profiler")
    def test_custom_columns_export(self, profiler_mock):
        profiler_mock.storage.fetch_all.return_value = [
            ViewProfiler(
                view_name="app.view_name", method="GET", anon_calls=8, cache_hits=3,
                sql_total_time=40, sql_total_count=20, total_calls=10, total_time=50,
            ),
        ]
        response = self.client.get(reverse("admin:speedinfo-profiler-export"))
        output = response.content.decode()

        self.assertEqual(
            output,
            "View name,HTTP method,Total calls,Time per call,Total time\r\n"
            "app.view_name,GET,10,5.00000000,50.0000\r\n",
        )

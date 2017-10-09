# coding: utf-8

import csv

from time import sleep

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from speedinfo import profiler, settings
from speedinfo.models import ViewProfiler


class ProfilerTest(TestCase):
    def setUp(self):
        cache.clear()
        profiler.is_on = True
        settings.SPEEDINFO_EXCLUDE_URLS = []

        self.class_view_url = reverse('class-view')
        self.cached_class_view_url = reverse('cached-class-view')
        self.func_view_url = reverse('func-view')
        self.cached_func_view_url = reverse('cached-func-view')

    def test_profiler_state(self):
        profiler.is_on = False
        self.client.get(self.func_view_url)
        self.assertFalse(ViewProfiler.objects.exists())

        profiler.switch()
        self.client.get(self.func_view_url)
        self.assertTrue(ViewProfiler.objects.exists())

    def test_view_name(self):
        # Broken url
        self.client.get('/404/')
        self.assertFalse(ViewProfiler.objects.exists())

        # Class-based views
        self.client.get(self.class_view_url)
        self.assertTrue(ViewProfiler.objects.filter(view_name='tests.views.ClassBasedView').exists())

        # Functional views
        self.client.get(self.func_view_url)
        self.assertTrue(ViewProfiler.objects.filter(view_name='tests.views.func_view').exists())

    def test_incrementing_counters(self):
        self.client.get(self.class_view_url)
        self.assertTrue(ViewProfiler.objects.exists())

        data = ViewProfiler.objects.first()
        self.assertEqual(data.anon_calls, 1)
        self.assertEqual(data.cache_hits, 0)
        self.assertEqual(data.total_calls, 1)
        self.assertTrue(data.total_time > 0)

        total_time = data.total_time
        self.client.get(self.class_view_url)
        data.refresh_from_db()

        self.assertEqual(data.anon_calls, 2)
        self.assertEqual(data.cache_hits, 0)
        self.assertEqual(data.total_calls, 2)
        self.assertTrue(data.total_time > total_time)

    def test_http_methods(self):
        self.client.get(self.func_view_url)
        self.assertTrue(ViewProfiler.objects.filter(view_name='tests.views.func_view', method='GET').exists())

        self.client.post(self.func_view_url)
        self.assertTrue(ViewProfiler.objects.filter(view_name='tests.views.func_view', method='POST').exists())

    def test_auth_calls(self):
        # Anonymous user
        self.client.get(self.func_view_url)

        data = ViewProfiler.objects.first()
        self.assertEqual(data.anon_calls, 1)
        self.assertEqual(data.total_calls, 1)

        # Authenticated user
        user = User.objects.create(username='user')
        self.client.force_login(user)
        self.client.get(self.func_view_url)

        data.refresh_from_db()
        self.assertEqual(data.anon_calls, 1)
        self.assertEqual(data.total_calls, 2)

    def test_per_view_cache(self):
        # First request doesn't hit cache
        self.client.get(self.cached_func_view_url)

        data = ViewProfiler.objects.first()
        self.assertEqual(data.cache_hits, 0)

        # Second request hit cache
        self.client.get(self.cached_func_view_url)
        data.refresh_from_db()
        self.assertEqual(data.cache_hits, 1)

        # Third request hit cache
        self.client.get(self.cached_func_view_url)
        data.refresh_from_db()
        self.assertEqual(data.cache_hits, 2)

        # Wait for the cache timeout
        sleep(3)
        self.client.get(self.cached_func_view_url)
        data.refresh_from_db()
        self.assertEqual(data.cache_hits, 2)

    def test_per_site_cache(self):
        with self.modify_settings(MIDDLEWARE={
            'append': 'django.middleware.cache.FetchFromCacheMiddleware',
            'prepend': 'django.middleware.cache.UpdateCacheMiddleware',
        }):
            self.client.get(self.func_view_url)
            data = ViewProfiler.objects.first()
            self.assertEqual(data.cache_hits, 0)

            self.client.get(self.func_view_url)
            data.refresh_from_db()
            self.assertEqual(data.cache_hits, 1)

    def test_custom_cache_flag(self):
        self.client.get(self.cached_class_view_url)
        data = ViewProfiler.objects.first()
        self.assertEqual(data.cache_hits, 1)

    def test_export(self):
        self.client.get(self.cached_func_view_url)
        self.client.get(self.cached_func_view_url)

        vp = ViewProfiler.objects.first()
        vp.sql_total_time = 1
        vp.sql_total_count = 6
        vp.total_time = 2
        vp.total_calls = 2
        vp.save()

        output = profiler.export()
        results = list(csv.reader(output.getvalue().splitlines()))
        self.assertEqual(results[0], ['View name', 'HTTP method', 'Total calls', 'Anonymous calls', 'Cache hits',
                                      'SQL queries per call', 'SQL time', 'Time per call', 'Total time'])
        self.assertEqual(results[1], ['tests.views.cached_func_view', 'GET', '2', '100.0%', '50.0%',
                                      '3', '50.0%', '1.0', '2.0'])

    def test_flush(self):
        self.client.get(self.class_view_url)
        self.client.get(self.func_view_url)
        self.assertEqual(ViewProfiler.objects.count(), 2)

        profiler.flush()
        self.assertFalse(ViewProfiler.objects.exists())

    def test_exclude_urls(self):
        settings.SPEEDINFO_EXCLUDE_URLS = [reverse('func-view')]

        self.client.get(self.func_view_url)
        self.assertFalse(ViewProfiler.objects.exists())

        self.client.get(self.cached_func_view_url)
        self.assertFalse(ViewProfiler.objects.exists())

        self.client.get(self.class_view_url)
        self.assertTrue(ViewProfiler.objects.exists())


class ProfilerAdminTest(TestCase):
    def setUp(self):
        cache.clear()
        settings.SPEEDINFO_EXCLUDE_URLS = []
        admin = User.objects.create_superuser(username='admin', email='', password='123456')
        self.client.force_login(admin)

    def test_switch_url(self):
        self.assertFalse(profiler.is_on)
        self.client.get(reverse('admin:speedinfo-profiler-switch'))

        self.assertTrue(profiler.is_on)
        self.client.get(reverse('admin:speedinfo-profiler-switch'))
        self.assertFalse(profiler.is_on)

    def test_export_url(self):
        self.client.get(reverse('class-view'))
        response = self.client.get(reverse('admin:speedinfo-profiler-export'))
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename=profiler.csv')
        self.assertEqual(response.content, profiler.export().getvalue())

    def test_flush_url(self):
        profiler.is_on = True
        settings.SPEEDINFO_EXCLUDE_URLS = [reverse('admin:index')]

        self.client.get(reverse('class-view'))
        self.assertTrue(ViewProfiler.objects.exists())

        self.client.get(reverse('admin:speedinfo-profiler-reset'))
        self.assertFalse(ViewProfiler.objects.exists())

    def test_permissions(self):
        profiler.is_on = True
        self.client.get(reverse('class-view'))

        response = self.client.get(reverse('admin:speedinfo_viewprofiler_add'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('admin:speedinfo_viewprofiler_change', args=(1,)))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('admin:speedinfo_viewprofiler_delete', args=(1,)))
        self.assertEqual(response.status_code, 403)

    def test_changelist(self):
        response = self.client.get(reverse('admin:speedinfo_viewprofiler_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('profiler_is_on' in response.context)

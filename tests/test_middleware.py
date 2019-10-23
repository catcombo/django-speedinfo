# coding: utf-8

import django
import mock
from django.contrib.auth.models import AnonymousUser, User
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, modify_settings, override_settings

from speedinfo.middleware import ProfilerMiddleware

try:
    from django.urls import reverse  # Django >= 1.10
except ImportError:
    from django.core.urlresolvers import reverse

if django.VERSION < (1, 10):
    MIDDLEWARE_SETTINGS_NAME = "MIDDLEWARE_CLASSES"
else:
    MIDDLEWARE_SETTINGS_NAME = "MIDDLEWARE"


@override_settings(
    SPEEDINFO_STORAGE="speedinfo.storage.cache.storage.CacheStorage",
    SPEEDINFO_TESTS=True,
)
@mock.patch("speedinfo.middleware.profiler")
class ProfilerMiddlewareTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_call_conditions(self, profiler_mock):
        profiler_mock.is_on = False
        self.client.get(reverse("func-view"))
        profiler_mock.storage.add.assert_not_called()

        profiler_mock.reset_mock()
        profiler_mock.is_on = True
        self.client.get(reverse("func-view"))
        profiler_mock.storage.add.assert_called_once()

        profiler_mock.reset_mock()
        self.client.get("/")
        profiler_mock.storage.add.assert_not_called()

        with mock.patch("speedinfo.middleware.conditions_dispatcher.get_conditions") as get_conditions_mock:
            get_conditions_mock.return_value = [
                mock.Mock(process_request=mock.Mock(return_value=False)),
            ]
            profiler_mock.reset_mock()
            self.client.get(reverse("func-view"))
            profiler_mock.storage.add.assert_not_called()

    def test_get_view_name(self, profiler_mock):
        profiler_mock.is_on = True

        self.client.get("/")
        profiler_mock.storage.add.assert_not_called()

        self.client.get(reverse("func-view"))
        self.assertEqual(profiler_mock.storage.add.call_args.kwargs["view_name"], "tests.views.func_view")

        self.client.get(reverse("class-view"))
        self.assertEqual(profiler_mock.storage.add.call_args.kwargs["view_name"], "tests.views.ClassBasedView")

    def test_request_method(self, profiler_mock):
        profiler_mock.is_on = True

        self.client.get(reverse("func-view"))
        self.assertEqual(profiler_mock.storage.add.call_args.kwargs["method"], "GET")

        self.client.post(reverse("func-view"))
        self.assertEqual(profiler_mock.storage.add.call_args.kwargs["method"], "POST")

    def test_request_user(self, profiler_mock):
        profiler_mock.is_on = True
        factory = RequestFactory()
        request = factory.get(reverse("func-view"))

        middleware = ProfilerMiddleware(get_response=HttpResponse)
        middleware(request)
        self.assertTrue(profiler_mock.storage.add.call_args.kwargs["is_anon_call"])

        request.user = AnonymousUser()
        middleware(request)
        self.assertTrue(profiler_mock.storage.add.call_args.kwargs["is_anon_call"])

        request.user = User.objects.create_user(username="user")
        middleware(request)
        self.assertFalse(profiler_mock.storage.add.call_args.kwargs["is_anon_call"])

    def test_cache_hit(self, profiler_mock):
        profiler_mock.is_on = True

        self.client.get(reverse("cached-attr-func-view"))
        self.assertTrue(profiler_mock.storage.add.call_args.kwargs["is_cache_hit"])

        self.client.get(reverse("cached-func-view"))
        self.assertFalse(profiler_mock.storage.add.call_args.kwargs["is_cache_hit"])

        self.client.get(reverse("cached-func-view"))
        self.assertTrue(profiler_mock.storage.add.call_args.kwargs["is_cache_hit"])

    @modify_settings(**{MIDDLEWARE_SETTINGS_NAME: {
        "append": "django.middleware.cache.FetchFromCacheMiddleware",
        "prepend": "django.middleware.cache.UpdateCacheMiddleware",
    }})
    def test_per_site_cache(self, profiler_mock):
        profiler_mock.is_on = True

        self.client.get(reverse("func-view"))
        self.assertFalse(profiler_mock.storage.add.call_args.kwargs["is_cache_hit"])

        self.client.get(reverse("func-view"))
        self.assertTrue(profiler_mock.storage.add.call_args.kwargs["is_cache_hit"])

    def test_sql_queries(self, profiler_mock):
        profiler_mock.is_on = True

        self.client.get(reverse("func-view"))
        self.assertEqual(profiler_mock.storage.add.call_args.kwargs["sql_count"], 0)

        self.client.get(reverse("db-func-view"))
        self.assertEqual(profiler_mock.storage.add.call_args.kwargs["sql_count"], 2)

# coding: utf-8

import django
from django.core.checks import run_checks
from django.test import TestCase, override_settings

if django.VERSION < (1, 10):
    MIDDLEWARE_SETTINGS_NAME = "MIDDLEWARE_CLASSES"
else:
    MIDDLEWARE_SETTINGS_NAME = "MIDDLEWARE"


class AppsTestCase(TestCase):
    def test_valid_config(self):
        messages = run_checks()
        self.assertEqual(messages, [])

    @override_settings(**{MIDDLEWARE_SETTINGS_NAME: [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ]})
    def test_missing_middleware(self):
        messages = run_checks()
        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].id, "speedinfo.W001")

    @override_settings(**{MIDDLEWARE_SETTINGS_NAME: [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
        "speedinfo.middleware.ProfilerMiddleware",
    ]})
    def test_cache_middleware_position(self):
        messages = run_checks()
        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].id, "speedinfo.E001")

    @override_settings(**{MIDDLEWARE_SETTINGS_NAME: [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "speedinfo.middleware.ProfilerMiddleware",
        "speedinfo.middleware.ProfilerMiddleware",
    ]})
    def test_multiple_middlewares(self):
        messages = run_checks()
        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].id, "speedinfo.E002")

    @override_settings(CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    })
    def test_missing_cache_backend(self):
        messages = run_checks()
        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].id, "speedinfo.E003")

    @override_settings(SPEEDINFO_STORAGE=None)
    def test_missing_storage(self):
        messages = run_checks()
        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].id, "speedinfo.E004")

    @override_settings(SPEEDINFO_STORAGE="invalid.module.path")
    def test_invalid_storage(self):
        messages = run_checks()
        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].id, "speedinfo.E005")

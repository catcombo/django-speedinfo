# coding: utf-8

from django.test import RequestFactory, TestCase, override_settings

from speedinfo.conditions.exclude_urls import ExcludeURLCondition


@override_settings(
    SPEEDINFO_STORAGE="speedinfo.storage.cache.storage.CacheStorage",
    SPEEDINFO_PROFILING_CONDITIONS=[
        "speedinfo.conditions.exclude_urls.ExcludeURLCondition",
    ],
    SPEEDINFO_EXCLUDE_URLS=["/weak/$", "/strict/"],
    SPEEDINFO_TESTS=True,
)
class ExcludeURLConditionTestCase(TestCase):
    def setUp(self):
        self.condition = ExcludeURLCondition()
        self.factory = RequestFactory()

    def test_mismatch(self):
        request = self.factory.get("/")
        self.assertTrue(self.condition.process_request(request))
        self.assertTrue(self.condition.process_response(request))

    def test_strict_match(self):
        request = self.factory.get("/strict/")
        self.assertFalse(self.condition.process_request(request))
        self.assertTrue(self.condition.process_response(request))

        request = self.factory.get("/strict/more/")
        self.assertFalse(self.condition.process_request(request))
        self.assertTrue(self.condition.process_response(request))

    def test_weak_match(self):
        request = self.factory.get("/weak/")
        self.assertFalse(self.condition.process_request(request))
        self.assertTrue(self.condition.process_response(request))

        request = self.factory.get("/weak/more/")
        self.assertTrue(self.condition.process_request(request))
        self.assertTrue(self.condition.process_response(request))

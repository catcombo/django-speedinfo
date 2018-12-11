# coding: utf-8

import re

from speedinfo.conditions.base import Condition
from speedinfo.settings import speedinfo_settings


class ExcludeURLCondition(Condition):
    """
    Plugin for conditional profiling based on the list of
    urls specified in SPEEDINFO_EXCLUDE_URLS settings
    """
    def __init__(self):
        self.patterns = None

    def get_patterns(self):
        if (self.patterns is None) or speedinfo_settings.SPEEDINFO_TESTS:
            self.patterns = [re.compile(pattern) for pattern in speedinfo_settings.SPEEDINFO_EXCLUDE_URLS]

        return self.patterns

    def process_request(self, request):
        """Checks requested page url against the list of excluded urls.

        :type request: :class:`django.http.HttpRequest`
        :return: False if path matches to any of the exclude urls
        :rtype: bool
        """
        for pattern in self.get_patterns():
            if pattern.match(request.path):
                return False

        return True

    def process_response(self, response):
        return True

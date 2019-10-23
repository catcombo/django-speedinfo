# coding: utf-8

import re

from speedinfo.conditions.base import AbstractCondition
from speedinfo.conf import speedinfo_settings


class ExcludeURLCondition(AbstractCondition):
    """
    Condition allows to exclude some urls from profiling by adding them
    to the SPEEDINFO_EXCLUDE_URLS list (default is empty). Each entry in
    SPEEDINFO_EXCLUDE_URLS is a regex compatible expression to test requested url.
    """
    def __init__(self):
        self.patterns = None

    def get_patterns(self):
        if (self.patterns is None) or speedinfo_settings.SPEEDINFO_TESTS:
            self.patterns = [re.compile(pattern) for pattern in speedinfo_settings.SPEEDINFO_EXCLUDE_URLS]

        return self.patterns

    def process_request(self, request):
        """Checks requested url against the list of excluded urls.

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

# coding: utf-8


class Condition:
    """
    Base class for user-defined profiling condition classes
    """
    def process_request(self, request):
        """
        :type request: :class:`django.http.HttpRequest`
        :return: False if requested page should be excluded from profiling
        :rtype: bool
        """
        raise NotImplementedError

    def process_response(self, response):
        """
        :type response: :class:`django.http.HttpResponse`
        :return: False if requested page should be excluded from profiling
        :rtype: bool
        """
        raise NotImplementedError

# coding: utf-8

from abc import ABCMeta, abstractmethod


class AbstractCondition(object):
    """
    Base class for user-defined profiling conditions.
    Condition is used to describe the rules used to filter
    views for profiling.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def process_request(self, request):
        """
        :type request: :class:`django.http.HttpRequest`
        :return: False if the requested page should not be profiled
        :rtype: bool
        """

    @abstractmethod
    def process_response(self, response):
        """
        :type response: :class:`django.http.HttpResponse`
        :return: False if the requested page should not be profiled
        :rtype: bool
        """

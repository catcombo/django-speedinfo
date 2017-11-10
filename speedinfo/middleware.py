# coding: utf-8

import re

from time import time
from django.db import connection
from speedinfo import profiler, settings

try:
    from django.urls import resolve, Resolver404  # Django >= 1.10
except ImportError:
    from django.core.urlresolvers import resolve, Resolver404


class ProfilerMiddleware(object):
    """
    Collects request and response statistics and saves profiler data.
    Unified middleware for all Django versions.
    """
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.force_debug_cursor = False
        self.start_time = 0
        self.exclude_urls_re = [re.compile(pattern) for pattern in settings.SPEEDINFO_EXCLUDE_URLS]

    def match_exclude_urls(self, path):
        """Looks for a match requested page url to the exclude urls list.

        :param str path: Path to the requested page, not including the scheme or domain
        :return: True if path matches to any of the exclude urls
        :rtype: bool
        """
        for url_re in self.exclude_urls_re:
            if url_re.match(path):
                return True

        return False

    def get_view_name(self, request):
        """Returns full view name from request, eg. 'app.module.view_name'.

        :param request: Request object
        :type request: :class:`django.http.HttpRequest`
        :return: view name or None if name can't be resolved
        :rtype: str or None
        """
        try:
            return resolve(request.path)._func_path
        except Resolver404:
            return None

    def process_view(self, request, *args, **kwargs):
        """Initialize statistics variables and environment.

        :return: Response object or None
        :rtype: :class:`django.http.HttpResponse` or None
        """
        if not profiler.is_on or self.match_exclude_urls(request.path):
            return

        # Force DB connection to debug mode to get sql time and number of queries
        self.force_debug_cursor = connection.force_debug_cursor
        connection.force_debug_cursor = True
        self.start_time = time()

    def process_response(self, request, response):
        """Aggregates request and response statistics and saves it in profiler data.

        :param request: Request object
        :type request: :class:`django.http.HttpRequest`
        :param response: Response object returned by a Django view or by a middleware
        :type response: :class:`django.http.HttpResponse` or :class:`django.http.StreamingHttpResponse`
        :return: View response
        :rtype: :class:`django.http.HttpResponse` or :class:`django.http.StreamingHttpResponse`
        """
        if not profiler.is_on or self.match_exclude_urls(request.path) or not hasattr(request, 'user'):
            return response

        duration = time() - self.start_time
        connection.force_debug_cursor = self.force_debug_cursor

        # Get SQL queries count and execution time
        sql_time = 0
        sql_count = len(connection.queries)
        for query in connection.queries:
            sql_time += float(query.get('time', 0))

        # Collects request and response params
        view_name = self.get_view_name(request)
        is_anon_call = request.user.is_anonymous()
        is_cache_hit = getattr(response, settings.SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, False)

        # Saves profiler data
        if view_name is not None:
            profiler.process(view_name, request.method, is_anon_call, is_cache_hit, sql_time, sql_count, duration)

        return response

    def __call__(self, request):
        """New middleware handler introduced in Django 1.10.

        :param request: Request object
        :type request: :class:`django.http.HttpRequest`
        :return: View response
        :rtype: :class:`django.http.HttpResponse` or :class:`django.http.StreamingHttpResponse`
        """
        response = self.process_view(request)

        if response is None:
            response = self.get_response(request)

        return self.process_response(request, response)

# coding: utf-8

import re

from time import time
from django.db import connection
from django.urls import resolve, Resolver404
from speedinfo import profiler, settings


class ProfilerMiddleware(object):
    """
    Collects request and response statistics and saves profiler data.
    """
    def __init__(self, get_response):
        self.get_response = get_response
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

    def __call__(self, request):
        """Collects request and response statistics and saves profiler data.

        :param request: Request object
        :type request: :class:`django.http.HttpRequest`
        :return: view response
        :rtype: :class:`django.http.HttpResponse`
        """
        if not profiler.is_on or self.match_exclude_urls(request.path):
            return self.get_response(request)

        # Force DB connection to debug mode to get sql time and number of queries
        force_debug_cursor = connection.force_debug_cursor
        connection.force_debug_cursor = True

        start_time = time()
        response = self.get_response(request)
        duration = time() - start_time

        connection.force_debug_cursor = force_debug_cursor

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

# coding: utf-8

from itertools import islice
from timeit import default_timer

from django.db import connection
from speedinfo import profiler
from speedinfo.conditions import conditions_dispatcher
from speedinfo.settings import speedinfo_settings

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
        self.is_active = False
        self.force_debug_cursor = False
        self.start_time = 0
        self.existing_sql_count = 0

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

    def can_process_request(self, request):
        """Checks conditions to start profiling the request

        :type request: :class:`django.http.HttpRequest`
        :return: True if request can be processed
        :rtype: bool
        """
        result = profiler.is_on and hasattr(request, 'user') and self.get_view_name(request)

        for condition in conditions_dispatcher.get_conditions():
            result = result and condition.process_request(request)

            if not result:
                break

        return result

    def can_process_response(self, response):
        """Checks conditions to finish profiling the request

        :type response: :class:`django.http.HttpResponse`
        :return: True if request can be processed
        :rtype: bool
        """
        result = True

        for condition in conditions_dispatcher.get_conditions():
            result = result and condition.process_response(response)

            if not result:
                break

        return result

    def process_view(self, request, *args, **kwargs):
        """Initialize statistics variables and environment.

        :return: Response object or None
        :rtype: :class:`django.http.HttpResponse` or None
        """
        self.is_active = self.can_process_request(request)

        if self.is_active:
            # Force DB connection to debug mode to get sql time and number of queries
            self.force_debug_cursor = connection.force_debug_cursor
            connection.force_debug_cursor = True

            self.existing_sql_count = len(connection.queries)
            self.start_time = default_timer()

    def process_response(self, request, response):
        """Aggregates request and response statistics and saves it in profiler data.

        :param request: Request object
        :type request: :class:`django.http.HttpRequest`
        :param response: Response object returned by a Django view or by a middleware
        :type response: :class:`django.http.HttpResponse` or :class:`django.http.StreamingHttpResponse`
        :return: View response
        :rtype: :class:`django.http.HttpResponse` or :class:`django.http.StreamingHttpResponse`
        """
        if self.is_active:
            if self.can_process_response(response):
                view_execution_time = default_timer() - self.start_time

                # Calculate the execution time and the number of queries.
                # Exclude queries made before the call of our middleware (e.g. in SessionMiddleware).
                sql_count = max(len(connection.queries) - self.existing_sql_count, 0)
                sql_time = sum(float(q['time']) for q in islice(connection.queries, self.existing_sql_count, None))

                # Collects request and response params
                view_name = self.get_view_name(request)
                is_anon_call = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
                is_cache_hit = getattr(response, speedinfo_settings.SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, False)

                # Saves profiler data
                profiler.data.add(view_name, request.method, is_anon_call, is_cache_hit, sql_time, sql_count, view_execution_time)

            # Rollback debug cursor value even if process response condition is disabled
            connection.force_debug_cursor = self.force_debug_cursor

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

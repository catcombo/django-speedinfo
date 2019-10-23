# coding: utf-8

from django.db import models

from speedinfo import profiler


class ViewProfilerQuerySet(models.QuerySet):
    """
    Overrides standard QuerySet behaviour to return objects
    from profiler storage. Hack is working only for `all()`,
    `order_by()` and `count()` methods and was made for integration
    with Django admin.
    """
    def _fetch_all(self):
        self._result_cache = profiler.storage.fetch_all(self.query.order_by)

    def count(self):
        return len(self)

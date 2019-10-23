# coding: utf-8

from django.db import models

from speedinfo.managers import ViewProfilerQuerySet


class ViewProfiler(models.Model):
    """
    Model doesn't have associated table in the database.
    So don't try to use it as an ordinary ORM model. You should
    think of it as a dataclass. Model is used for wrapping
    storage data and Django admin integration.
    """
    view_name = models.CharField("View name", max_length=255)
    method = models.CharField("HTTP method", max_length=8)
    anon_calls = models.PositiveIntegerField("Anonymous calls", default=0)
    cache_hits = models.PositiveIntegerField("Cache hits", default=0)
    sql_total_time = models.FloatField("SQL total time", default=0)
    sql_total_count = models.PositiveIntegerField("SQL total queries count", default=0)
    total_calls = models.PositiveIntegerField("Total calls", default=0)
    total_time = models.FloatField("Total time", default=0)

    objects = ViewProfilerQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "Views"
        managed = False

    def __init__(self, *args, **kwargs):
        # Extract extra fields from parameters
        extra_fields = {}
        model_field_names = [field.attname for field in self._meta.get_fields()]

        for field_name in list(kwargs):
            if field_name not in model_field_names:
                extra_fields[field_name] = kwargs.pop(field_name)

        super(ViewProfiler, self).__init__(*args, **kwargs)

        # Assign extra fields to the object if the field names
        # do not override existing fields
        for field_name, value in extra_fields.items():
            if not getattr(self, field_name, None):
                setattr(self, field_name, value)

    @property
    def anon_calls_ratio(self):
        """Anonymous calls ratio.

        :return: anonymous calls ratio percent
        :rtype: float
        """
        if self.total_calls > 0:
            return 100 * self.anon_calls / float(self.total_calls)
        else:
            return 0

    @property
    def cache_hits_ratio(self):
        """Cache hits ratio.

        :return: cache hits ratio percent
        :rtype: float
        """
        if self.total_calls > 0:
            return 100 * self.cache_hits / float(self.total_calls)
        else:
            return 0

    @property
    def sql_time_ratio(self):
        """SQL time per call ratio.

        :return: SQL time per call ratio percent
        :rtype: float
        """
        if self.total_time > 0:
            return 100 * self.sql_total_time / float(self.total_time)
        else:
            return 0

    @property
    def sql_count_per_call(self):
        """SQL queries count per call.

        :return: SQL queries count per call
        :rtype: int
        """
        if self.total_calls > 0:
            return int(round(self.sql_total_count / float(self.total_calls)))
        else:
            return 0

    @property
    def time_per_call(self):
        """Time per call.

        :return: time per call
        :rtype: float
        """
        if self.total_calls > 0:
            return self.total_time / float(self.total_calls)
        else:
            return 0

# coding: utf-8

from django.db import IntegrityError
from django.db.models import ExpressionWrapper, F, FloatField, IntegerField
from django.forms import model_to_dict

from speedinfo.models import ViewProfiler
from speedinfo.storage.base import AbstractStorage
from speedinfo.storage.database.models import Storage


class DatabaseStorage(AbstractStorage):
    def add(self, view_name, method, is_anon_call, is_cache_hit, sql_time, sql_count, view_execution_time):
        try:
            vp, created = Storage.objects.get_or_create(view_name=view_name, method=method)
        except IntegrityError:
            # IntegrityError raised in the case of concurrent access
            # to get_or_create method from another application worker/thread
            vp = Storage.objects.get(view_name=view_name, method=method)

        vp.anon_calls = F("anon_calls") + (is_anon_call and 1 or 0)
        vp.cache_hits = F("cache_hits") + (is_cache_hit and 1 or 0)
        vp.sql_total_time = F("sql_total_time") + sql_time
        vp.sql_total_count = F("sql_total_count") + sql_count
        vp.total_calls = F("total_calls") + 1
        vp.total_time = F("total_time") + view_execution_time
        vp.save()

    def fetch_all(self, ordering=None):
        qs = Storage.objects.annotate(
            anon_calls_ratio=ExpressionWrapper(100.0 * F("anon_calls") / F("total_calls"), output_field=FloatField()),
            cache_hits_ratio=ExpressionWrapper(100.0 * F("cache_hits") / F("total_calls"), output_field=FloatField()),
            sql_count_per_call=ExpressionWrapper(F("sql_total_count") / F("total_calls"), output_field=IntegerField()),
            sql_time_ratio=ExpressionWrapper(100.0 * F("sql_total_time") / F("total_time"), output_field=FloatField()),
            time_per_call=ExpressionWrapper(F("total_time") / F("total_calls"), output_field=FloatField()),
        )

        if ordering:
            qs = qs.order_by(*ordering)

        return [ViewProfiler(**model_to_dict(item)) for item in qs]

    def reset(self):
        Storage.objects.all().delete()

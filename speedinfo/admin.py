# coding: utf-8

import csv

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import F, FloatField, ExpressionWrapper
from django.http import HttpResponseRedirect, HttpResponse

from speedinfo import profiler, settings
from speedinfo.models import ViewProfiler

try:
    from django.urls import reverse  # Django >= 1.10
except ImportError:
    from django.core.urlresolvers import reverse


class ViewProfilerAdmin(admin.ModelAdmin):
    list_display_links = None
    actions = None
    ordering = ('-total_time',)

    class Media:
        css = {
            'all': ('speedinfo/css/admin.css',)
        }

    def get_queryset(self, request):
        qs = super(ViewProfilerAdmin, self).get_queryset(request)
        return qs.annotate(
            percall=ExpressionWrapper(F('total_time') / F('total_calls'), output_field=FloatField())
        )

    def get_list_display(self, request):
        """Creates and returns list of callables to represent
        model field values with a custom format.

        :param request: Request object
        :type request: :class:`django.http.HttpRequest`
        :return: list containing fields to be displayed on the changelist
        """
        list_display = []

        for rc in settings.SPEEDINFO_REPORT_COLUMNS_FORMAT:
            if rc.attr_name in settings.SPEEDINFO_REPORT_COLUMNS:

                def wrapper(col):
                    def field_format(obj):
                        return col.format.format(getattr(obj, col.attr_name))
                    field_format.short_description = col.name
                    field_format.admin_order_field = col.order_field

                    return field_format

                list_display.append(
                    wrapper(rc)
                )

        return list_display

    def change_view(self, *args, **kwargs):
        raise PermissionDenied

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return super(ViewProfilerAdmin, self).changelist_view(request, extra_context={
            'title': 'Views profiler',
            'profiler_is_on': profiler.is_on,
        })

    def get_urls(self):
        return [
            url(r'^switch/$', self.admin_site.admin_view(self.switch), name='speedinfo-profiler-switch'),
            url(r'^export/$', self.admin_site.admin_view(self.export), name='speedinfo-profiler-export'),
            url(r'^reset/$', self.admin_site.admin_view(self.reset), name='speedinfo-profiler-reset'),
        ] + super(ViewProfilerAdmin, self).get_urls()

    def switch(self, request):
        profiler.is_on = not profiler.is_on
        return HttpResponseRedirect(reverse('admin:speedinfo_viewprofiler_changelist'))

    def export(self, request):
        """Exports profiling data as a comma-separated file.

        :param request: :class:`django.http.HttpRequest`
        :return: comma-separated file
        :rtype: :class:`django.http.HttpResponse`
        """
        output = StringIO()
        export_columns = list(filter(lambda col: col.attr_name in settings.SPEEDINFO_REPORT_COLUMNS,
                                     settings.SPEEDINFO_REPORT_COLUMNS_FORMAT))

        csv_writer = csv.writer(output)
        csv_writer.writerow([col.name for col in export_columns])

        for row in profiler.data.all():
            csv_writer.writerow([
                col.format.format(getattr(row, col.attr_name))
                for col in export_columns
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=profiler.csv'

        return response

    def reset(self, request):
        profiler.data.reset()
        return HttpResponseRedirect(reverse('admin:speedinfo_viewprofiler_changelist'))


admin.site.register(ViewProfiler, ViewProfilerAdmin)

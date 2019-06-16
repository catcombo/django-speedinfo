# coding: utf-8

import csv

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse

from speedinfo import profiler
from speedinfo.models import ViewProfiler
from speedinfo.settings import speedinfo_settings

try:
    from django.urls import reverse  # Django >= 1.10
except ImportError:
    from django.core.urlresolvers import reverse


def field_wrapper(col):
    """Helper function to dynamically create list display method
    for :class:`ViewProfilerAdmin` to control value formating
    and sort order.

    :type col: :data:`settings.ReportColumnFormat`
    :rtype: function
    """
    def field_format(obj):
        return col.format.format(getattr(obj, col.attr_name))

    field_format.short_description = col.name
    field_format.admin_order_field = col.attr_name

    return field_format


class ViewProfilerAdmin(admin.ModelAdmin):
    list_display_links = None
    actions = None
    ordering = ('-total_time',)

    class Media:
        css = {
            'all': ('speedinfo/css/admin.css',)
        }

    def __init__(self, *args, **kwargs):
        """Initializes the list of visible columns and
        the way they are formating the values.
        """
        super(ViewProfilerAdmin, self).__init__(*args, **kwargs)
        self.list_display = []

        for rc in speedinfo_settings.SPEEDINFO_REPORT_COLUMNS_FORMAT:
            if rc.attr_name in speedinfo_settings.SPEEDINFO_REPORT_COLUMNS:
                method_name = '{}_wrapper'.format(rc.attr_name)
                setattr(self, method_name, field_wrapper(rc))
                self.list_display.append(method_name)

    def get_queryset(self, request):
        qs = super(ViewProfilerAdmin, self).get_queryset(request)

        for rc in speedinfo_settings.SPEEDINFO_REPORT_COLUMNS_FORMAT:
            if (rc.attr_name in speedinfo_settings.SPEEDINFO_REPORT_COLUMNS) and not isinstance(rc.expression, str):
                qs = qs.annotate(**{
                    rc.attr_name: rc.expression
                })

        return qs

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
        export_columns = list(filter(lambda col: col.attr_name in speedinfo_settings.SPEEDINFO_REPORT_COLUMNS,
                                     speedinfo_settings.SPEEDINFO_REPORT_COLUMNS_FORMAT))

        csv_writer = csv.writer(output)
        csv_writer.writerow([col.name for col in export_columns])

        for row in self.get_queryset(request):
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

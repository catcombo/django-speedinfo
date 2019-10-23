# coding: utf-8

import csv

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect

from speedinfo import profiler
from speedinfo.conf import speedinfo_settings
from speedinfo.models import ViewProfiler

try:
    from django.urls import reverse  # Django >= 1.10
except ImportError:
    from django.core.urlresolvers import reverse


def field_wrapper(col):
    """Helper function to dynamically create list display method
    for :class:`ViewProfilerAdmin` to control value formatting
    and sort order.

    :type col: tuple(str, str, str)
    :rtype: function
    """
    def field_format(obj):
        return col[1].format(getattr(obj, col[2]))

    field_format.short_description = col[0]
    field_format.admin_order_field = col[2]

    return field_format


class ViewProfilerAdmin(admin.ModelAdmin):
    list_display_links = None
    actions = None
    ordering = ("-total_time",)

    class Media:
        css = {
            "all": ("speedinfo/css/admin.css",),
        }

    def __init__(self, *args, **kwargs):
        """Initializes the list of visible columns and
        the way they are formatting the values.
        """
        super(ViewProfilerAdmin, self).__init__(*args, **kwargs)
        self.list_display = []

        for rc in speedinfo_settings.SPEEDINFO_ADMIN_COLUMNS:
            method_name = "{}_wrapper".format(rc[2])
            setattr(self, method_name, field_wrapper(rc))
            self.list_display.append(method_name)

    def change_view(self, *args, **kwargs):
        raise PermissionDenied

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return super(ViewProfilerAdmin, self).changelist_view(request, extra_context={
            "title": "Views profiler",
            "profiler_is_on": profiler.is_on,
        })

    def get_urls(self):
        return [
            url(r"^switch/$", self.admin_site.admin_view(self.switch), name="speedinfo-profiler-switch"),
            url(r"^export/$", self.admin_site.admin_view(self.export), name="speedinfo-profiler-export"),
            url(r"^reset/$", self.admin_site.admin_view(self.reset), name="speedinfo-profiler-reset"),
        ] + super(ViewProfilerAdmin, self).get_urls()

    def switch(self, request):
        profiler.is_on = not profiler.is_on
        return HttpResponseRedirect(reverse("admin:speedinfo_viewprofiler_changelist"))

    def export(self, request):
        """Exports profiling data as a comma-separated file.

        :param request: :class:`django.http.HttpRequest`
        :return: comma-separated file
        :rtype: :class:`django.http.HttpResponse`
        """
        output = StringIO()
        csv_writer = csv.writer(output)
        csv_writer.writerow([col[0] for col in speedinfo_settings.SPEEDINFO_ADMIN_COLUMNS])

        for row in self.get_queryset(request):
            csv_writer.writerow([
                col[1].format(getattr(row, col[2]))
                for col in speedinfo_settings.SPEEDINFO_ADMIN_COLUMNS
            ])

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=profiler.csv"

        return response

    def reset(self, request):
        profiler.storage.reset()
        return HttpResponseRedirect(reverse("admin:speedinfo_viewprofiler_changelist"))


admin.site.register(ViewProfiler, ViewProfilerAdmin)

# coding: utf-8

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
    list_display = settings.SPEEDINFO_REPORT_COLUMNS
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

    def anon_calls_ratio(self, obj):
        return '{:.1f} %'.format(obj.anon_calls_ratio)
    anon_calls_ratio.short_description = 'Anonymous calls'

    def cache_hits_ratio(self, obj):
        return '{:.1f} %'.format(obj.cache_hits_ratio)
    cache_hits_ratio.short_description = 'Cache hits'

    def sql_count_per_call(self, obj):
        return obj.sql_count_per_call
    sql_count_per_call.short_description = 'SQL queries per call'

    def sql_time_ratio(self, obj):
        return '{:.1f} %'.format(obj.sql_time_ratio)
    sql_time_ratio.short_description = 'SQL time'

    def time_per_call(self, obj):
        return obj.time_per_call
    time_per_call.short_description = 'Time per call'
    time_per_call.admin_order_field = 'percall'

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
        profiler.switch()
        return HttpResponseRedirect(reverse('admin:speedinfo_viewprofiler_changelist'))

    def export(self, request):
        output = profiler.export()
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=profiler.csv'

        return response

    def reset(self, request):
        profiler.flush()
        return HttpResponseRedirect(reverse('admin:speedinfo_viewprofiler_changelist'))


admin.site.register(ViewProfiler, ViewProfilerAdmin)

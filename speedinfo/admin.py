# coding: utf-8

from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import F, FloatField, ExpressionWrapper
from django.http import HttpResponseRedirect
from django.urls import reverse

from speedinfo import profiler
from speedinfo.models import ViewProfiler


class ViewProfilerAdmin(admin.ModelAdmin):
    list_display = ('view_name', 'method', 'anon_calls_ratio', 'cache_hits_ratio',
                    'total_calls', 'percall', 'total_time')
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
        return '{:.1f} %'.format(100 * obj.anon_calls / float(obj.total_calls))
    anon_calls_ratio.short_description = 'Anonymous calls'

    def cache_hits_ratio(self, obj):
        return '{:.1f} %'.format(100 * obj.cache_hits / float(obj.total_calls))
    cache_hits_ratio.short_description = 'Cache hits'

    def percall(self, obj):
        return obj.percall
    percall.short_description = 'Time per call'
    percall.admin_order_field = 'percall'

    def change_view(self, *args, **kwargs):
        raise PermissionDenied

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return super(ViewProfilerAdmin, self).changelist_view(request, extra_context={
            'profiler_is_on': profiler.is_on,
        })

    def get_urls(self):
        return [
            url(r'^switch/$', self.admin_site.admin_view(self.switch), name='speedinfo-profiler-switch'),
            url(r'^reset/$', self.admin_site.admin_view(self.reset), name='speedinfo-profiler-reset'),
        ] + super(ViewProfilerAdmin, self).get_urls()

    def switch(self, request):
        profiler.switch()
        return HttpResponseRedirect(reverse('admin:speedinfo_viewprofiler_changelist'))

    def reset(self, request):
        profiler.flush()
        return HttpResponseRedirect(reverse('admin:speedinfo_viewprofiler_changelist'))


admin.site.register(ViewProfiler, ViewProfilerAdmin)

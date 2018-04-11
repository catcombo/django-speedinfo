# coding: utf-8

from django.conf.urls import url
from django.contrib import admin

from .views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^cls/$', ClassBasedView.as_view(), name='class-view'),
    url(r'^cls/cached/$', CachedView.as_view(), name='cached-class-view'),
    url(r'^func/$', func_view, name='func-view'),
    url(r'^func/cached/$', cached_func_view, name='cached-func-view'),
    url(r'^func/db/$', db_func_view, name='db-func-view')
]

# coding: utf-8

from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r"^admin/", admin.site.urls),

    url(r"^cls/$", views.ClassBasedView.as_view(), name="class-view"),
    url(r"^func/$", views.func_view, name="func-view"),
    url(r"^func/cached/$", views.cached_func_view, name="cached-func-view"),
    url(r"^func/cached/attr/$", views.cached_attr_func_view, name="cached-attr-func-view"),
    url(r"^func/db/$", views.db_func_view, name="db-func-view"),
]

# coding: utf-8

from time import sleep

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.cache import cache_page

from speedinfo.settings import speedinfo_settings


class ClassBasedView(View):
    def get(self, request, *args, **kwargs):
        sleep(0.1)
        return HttpResponse()


class CachedView(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse()
        setattr(response, speedinfo_settings.SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, True)
        return response


def func_view(request):
    return HttpResponse()


@cache_page(2)
def cached_func_view(request):
    return HttpResponse()


def db_func_view(request):
    User.objects.create_user(username='user', password='123456')
    User.objects.get(username='user')
    return HttpResponse()

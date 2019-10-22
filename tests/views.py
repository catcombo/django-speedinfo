# coding: utf-8

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.generic import View

from speedinfo.conf import speedinfo_settings


class ClassBasedView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()


def func_view(request):
    return HttpResponse()


def cached_attr_func_view(request):
    response = HttpResponse()
    setattr(response, speedinfo_settings.SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, True)
    return response


@cache_page(30)
def cached_func_view(request):
    return HttpResponse()


def db_func_view(request):
    User.objects.create_user(username="user")
    User.objects.get(username="user")
    return HttpResponse()

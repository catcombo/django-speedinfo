# coding: utf-8

import django.core.cache

from speedinfo.profiler import Profiler
from speedinfo.proxy import ProfilerCacheHandler

django.core.cache.caches = ProfilerCacheHandler()
profiler = Profiler()

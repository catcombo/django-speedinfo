# django-speedinfo


[![Build Status](https://travis-ci.org/catcombo/django-speedinfo.svg?branch=master)](https://travis-ci.org/catcombo/django-speedinfo)

SpeedInfo is a live profiling tool for the Django framework to find
the most high loaded views in your project for the next optimization.
SpeedInfo counts number of calls, cache hits, SQL queries,
measures average and total call time and more for each of your views.
Detailed report and profiler controls are available in Django admin.

![Speedinfo admin screenshot](https://github.com/catcombo/django-speedinfo/raw/master/screenshots/main.png)


# Installation

1. Run `pip install django-speedinfo`.
2. Add `speedinfo` to `INSTALLED_APPS`.
3. Add `speedinfo.middleware.ProfilerMiddleware` to the end of `MIDDLEWARE` (or `MIDDLEWARE_CLASSES` for Django < 1.10) 
list, but before `django.middleware.cache.FetchFromCacheMiddleware` (if used):
    ```
    MIDDLEWARE = [
        ...,
        'speedinfo.middleware.ProfilerMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
    ]
    ```
4. Setup any cache backend, except local-memory and dummy caching, using our proxy cache backend. Speedinfo needs cache 
to store profiler state between requests and to intercept calls to cache:
    ```
    CACHES = {
        'default': {
            'BACKEND': 'speedinfo.backends.proxy_cache',
            'CACHE_BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
        }
    }
    ```
5. Run `python manage.py migrate`.
6. Run `python manage.py collectstatic`.


# Usage

Open `Views profiler` in Django admin. Click the `Turn on` / `Turn off` button
to control profiler state. Press `Reset` button to reset all data.


# Configuration

`SpeedInfo` automatically detects when using Django per-site caching via
`UpdateCacheMiddleware` and `FetchFromCacheMiddleware` middlewares
or per-view caching via `cache_page` decorator and counts cache hit
when retrieving page from cache.

If you implement your own caching logic and want to mark
view response as obtained from a cache, add attribute to the `HttpResponse` object
with the name from `SPEEDINFO_CACHED_RESPONSE_ATTR_NAME` and the value set to True.
Example:
```
from django.views import View
from speedinfo.settings import SPEEDINFO_CACHED_RESPONSE_ATTR_NAME

class CachedView(View):
    def get(self, request, *args, **kwargs):
        # ...
        # `response` was taken from the cache
        # mark it in appropriate way
        setattr(response, SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, True)
        return response
```
Change `SPEEDINFO_REPORT_COLUMNS` setting to customize Django admin profiler columns.
Default value:
```
SPEEDINFO_REPORT_COLUMNS = (
    'view_name', 'method', 'anon_calls_ratio', 'cache_hits_ratio',
    'sql_count_per_call', 'sql_time_ratio', 'total_calls', 'time_per_call', 'total_time'
)
```


# Profiling conditions

`SPEEDINFO_PROFILING_CONDITIONS` setting allows to declare a list of imported classes
to define the conditions for profiling a processed view. By default, the only condition is enabled:
```
SPEEDINFO_PROFILING_CONDITIONS = [
    'speedinfo.conditions.exclude_urls.ExcludeURLCondition',
]
```

`ExcludeURLCondition` allows you to exclude some urls from profiling by adding them to
the `SPEEDINFO_EXCLUDE_URLS` list. `ExcludeURLCondition` uses `re.match` internally to test
requested url. Example:
```
SPEEDINFO_EXCLUDE_URLS = [
    r'/admin/',
    r'/news/$',
    r'/movie/\d+/$',
]
```

To define your own condition class, you must inherit from the base class `speedinfo.conditions.base.Condition`
and implement all abstract methods. See `ExcludeURLCondition` source code for implementation example. Then add
full path to your class to `SPEEDINFO_PROFILING_CONDITIONS` list as shown above. Conditions in mentioned list
are executed in a top-down order. The first condition returning `False` interrupts the further check.


# Profiler storage

If you want to use different database to store `django-speedinfo` data:

1. Define separate database in `DATABASES` option in the [project settings](https://docs.djangoproject.com/en/2.2/topics/db/multi-db/).
2. Configure [database router](https://docs.djangoproject.com/en/2.2/topics/db/multi-db/#automatic-database-routing) 
to return appropriate database for `speedinfo` application (see an example in documentation).


# Notice

The number of SQL queries measured by `django-speedinfo` may differ from the values
of `django-debug-toolbar` for the same view. It happens because we show the average number
of SQL queries for each view. Secondly, we don't take into account SQL queries
made before the call of a view (e.g. in the preceding middlewares), as well SQL queries
made after the view call.

# django-speedinfo

[![Build Status](https://travis-ci.org/catcombo/django-speedinfo.svg?branch=master)](https://travis-ci.org/catcombo/django-speedinfo)
[![Coverage Status](https://coveralls.io/repos/github/catcombo/django-speedinfo/badge.svg?branch=master)](https://coveralls.io/github/catcombo/django-speedinfo?branch=master)

`django-speedinfo` is a live profiling tool for Django projects to find
the most high loaded views for the next optimization. `django-speedinfo` counts
number of calls, cache hits, SQL queries, measures average and total call time
and more for each of your views. Detailed report and profiler controls are
available in Django admin.

![Speedinfo admin screenshot](https://github.com/catcombo/django-speedinfo/raw/master/screenshots/main.png)


# Prerequisites

- Python 2.7, 3.6+
- Django 1.8+


# Installation

```
pip install django-speedinfo
```

# Upgrading from 1.x

Old profiling data will be unavailable after upgrading. Don't forget to export the data in advance.

- Setup one of the storage backends as shown in the section 4 of [Setup](#setup) below.
- `SPEEDINFO_PROFILING_CONDITIONS` is empty by default. If you use `SPEEDINFO_EXCLUDE_URLS` in your
  project you need to initialize the list of conditions explicitly:
  `SPEEDINFO_PROFILING_CONDITIONS = ["speedinfo.conditions.exclude_urls.ExcludeURLCondition"]`
- `SPEEDINFO_REPORT_COLUMNS` and `SPEEDINFO_REPORT_COLUMNS_FORMAT` were removed, use `SPEEDINFO_ADMIN_COLUMNS` instead.
  Every entry in `SPEEDINFO_ADMIN_COLUMNS` list is a tuple (column name, value format, attribute name).
  See [Customize admin columns](#customize-admin-columns) for details. To add extra columns
  follow the instruction in the section [Extra admin columns](#extra-admin-columns) below.
- `speedinfo.settings` module renamed to `speedinfo.conf`
- Base condition class was renamed from `Condition` to `AbstractCondition`


# Setup

1. Add `speedinfo` to `INSTALLED_APPS`.
2. Add `speedinfo.middleware.ProfilerMiddleware` to the end of `MIDDLEWARE` (or `MIDDLEWARE_CLASSES` for Django < 1.10) 
list, but before `django.middleware.cache.FetchFromCacheMiddleware` (if used):
    ```
    MIDDLEWARE = [
        ...,
        "speedinfo.middleware.ProfilerMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
    ]
    ```
3. Setup any cache backend (except local-memory and dummy caching) using our proxy cache backend.
`django-speedinfo` needs the cache to store profiler state between requests and to intercept calls to cache:
    ```
    CACHES = {
        "default": {
            "BACKEND": "speedinfo.backends.proxy_cache",
            "CACHE_BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": "/var/tmp/django_cache",
        }
    }
    ```
4. Setup storage for profiling data. `django-speedinfo` comes with two storages to choose from:
    - **Database storage**
        1. Add `speedinfo.storage.database` to `INSTALLED_APPS`.
        2. Add `SPEEDINFO_STORAGE = "speedinfo.storage.database.storage.DatabaseStorage"` to project settings.
        3. Run `python manage.py migrate`.
    - **Cache storage**
        1. Add `SPEEDINFO_STORAGE = "speedinfo.storage.cache.storage.CacheStorage"` to project settings.
        2. Optionally you may define a separate cache in `CACHES` to store profiling data.
           To use it in `CacheStorage` assign `SPEEDINFO_CACHE_STORAGE_CACHE_ALIAS` to the appropriate cache alias.
           Example:
            ```
            CACHES = {
                "default": {
                    "BACKEND": "speedinfo.backends.proxy_cache",
                    "CACHE_BACKEND": "django.core.cache.backends.db.DatabaseCache",
                    "LOCATION": "cache_table",
                },
                "speedinfo-storage": {
                    "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
                    "LOCATION": "127.0.0.1:11211",
                },
            })
            
            SPEEDINFO_CACHE_STORAGE_CACHE_ALIAS = "speedinfo-storage"
            ```
5. Run `python manage.py collectstatic`.


# Usage

Open `Views profiler` in Django admin. Click the `Turn on` / `Turn off` button
to control profiler state. Press `Reset` button to delete all profiling data.


# Advanced features

## Custom page caching

`django-speedinfo` automatically detects when Django use per-site caching via
`UpdateCacheMiddleware` and `FetchFromCacheMiddleware` middlewares
or per-view caching via `cache_page` decorator and counts cache hit
when retrieving pages from the cache.

If you implement your own caching logic and want to mark the view response
as obtained from the cache, add specified attribute to the `HttpResponse` object
as shown below:
```
from django.views import View
from from speedinfo.conf import speedinfo_settings

class CachedView(View):
    def get(self, request, *args, **kwargs):
        # ...
        # Assume that `response` was taken from the cache
        setattr(response, speedinfo_settings.SPEEDINFO_CACHED_RESPONSE_ATTR_NAME, True)
        return response
```
The default value of `SPEEDINFO_CACHED_RESPONSE_ATTR_NAME` is `_is_cached`.
But you can override it if the attribute name is conflicts with your application logic.

## Customize admin columns

`SPEEDINFO_ADMIN_COLUMNS` allows to control visibility and appearance of Django admin
profiler columns. Every entry in the `SPEEDINFO_ADMIN_COLUMNS` list is a tuple of
(column name, value format, `ViewProfiler` attribute name). Default value:
```
SPEEDINFO_ADMIN_COLUMNS = (
    ("View name", "{}", "view_name"),
    ("HTTP method", "{}", "method"),
    ("Anonymous calls", "{:.1f}%", "anon_calls_ratio"),
    ("Cache hits", "{:.1f}%", "cache_hits_ratio"),
    ("SQL queries per call", "{}", "sql_count_per_call"),
    ("SQL time", "{:.1f}%", "sql_time_ratio"),
    ("Total calls", "{}", "total_calls"),
    ("Time per call", "{:.8f}", "time_per_call"),
    ("Total time", "{:.4f}", "total_time"),
)
```

## Extra admin columns

To add additional data to a storage and columns to admin follow the instruction:

1. Create [custom storage backend](#custom-storage-backend) which will hold or calculate
   additional fields.
2. Implement storage `fetch_all()` method that will return the list of the `ViewProfiler`
   instances initialized with the extra fields. Example:
   ```
   def fetch_all(self, ordering=None):
       ...
       return [
           ViewProfiler(view_name="...", method="...", ..., extra_field="...")
           ...
       ]
   ```
3. Implement sorting by extra fields in `fetch_all()` method.
4. Add extra fields to `SPEEDINFO_ADMIN_COLUMNS` as described in the section
   [Customize admin columns](#customize-admin-columns).

## Profiling conditions

`SPEEDINFO_PROFILING_CONDITIONS` allows to declare a list of condition classes
to filter profiling views by some rules. By default `SPEEDINFO_PROFILING_CONDITIONS` is empty.
`django-speedinfo` comes with one build-in condition - `ExcludeURLCondition`. It allows to
exclude some urls from profiling by adding them to the `SPEEDINFO_EXCLUDE_URLS` list.
Each entry in `SPEEDINFO_EXCLUDE_URLS` is a regex compatible expression to test requested url.
Usage example:
```
SPEEDINFO_PROFILING_CONDITIONS = [
    "speedinfo.conditions.exclude_urls.ExcludeURLCondition",
]

SPEEDINFO_EXCLUDE_URLS = [
    r"/admin/",
    r"/news/$",
    r"/movie/\d+/$",
]
```

To define your own condition class, you must inherit from the base class `speedinfo.conditions.base.AbstractCondition`
and implement all abstract methods. See `ExcludeURLCondition` source code for implementation example. Then add
full path to your class to `SPEEDINFO_PROFILING_CONDITIONS` list as shown above. Conditions in mentioned list
are executed in a top-down order. The first condition returning `False` interrupts the further check.

## Custom storage backend

`django-speedinfo` comes with `DatabaseStorage` and `CacheStorage`. But you may want to write your
own storage (e.g. for MongoDB, Redis or even file-based). First create the storage class based on
`speedinfo.storage.base.AbstractStorage` and implement all abstract methods. See `speedinfo.storage.cache.storage`
and `speedinfo.storage.database.storage` as an examples. Then add path to your custom storage class
to the project settings `SPEEDINFO_STORAGE = "path.to.module.CustomStorage"`. Use our tests
to make sure that everything works as intended (you need to clone repository to get access to the `tests` package):
```
from django.test import TestCase, override_settings
from tests.test_storage import StorageTestCase

@override_settings(
    SPEEDINFO_STORAGE="path.to.module.CustomStorage",
    SPEEDINFO_TESTS=True,
)
class CustomStorageTestCase(StorageTestCase, TestCase):
    pass
```


# Notice

The number of SQL queries measured by `django-speedinfo` may differ from the values
of `django-debug-toolbar` for the same view. It happens because `django-speedinfo`
shows the average number of SQL queries for each view. Also profiler doesn't take
into account SQL queries made in the preceding middlewares.

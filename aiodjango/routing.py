import asyncio
import inspect
import re

from importlib import import_module

from django.conf import settings
from django.contrib.admindocs.views import extract_views_from_urlpatterns
from django.core.urlresolvers import reverse

from aiohttp.web import DynamicRoute


class DjangoRegexRoute(DynamicRoute):
    """Compatibility shim between routing frameworks."""

    def __init__(self, method, handler, name, regex, *, expect_handler=None):
        if not regex.lstrip('^').startswith('/'):
            regex = '^/' + regex.lstrip('^')
        pattern = re.compile(regex)
        super().__init__(method, handler, name, pattern, None, expect_handler=expect_handler)

    def url(self, *, parts, query=None):
        url = reverse(self.name, kwargs=parts)
        return self._append_query(url, query)

    def __repr__(self):
        name = "'" + self.name + "' " if self.name is not None else ""
        return ("<DjangoRegexRoute {name}[{method}] -> {handler!r}"
                .format(name=name, method=self.method, handler=self.handler))


def get_aio_routes(patterns=None):
    """Walk the URL patterns to find any coroutine views."""

    if patterns is None:
        urlconf = import_module(settings.ROOT_URLCONF)
        patterns = urlconf.urlpatterns
    routes = []
    view_functions = extract_views_from_urlpatterns(patterns)
    for (func, regex, namespace, name) in view_functions:
        if asyncio.iscoroutinefunction(func) or inspect.isgeneratorfunction(func):
            routes.append(DjangoRegexRoute('*', func, name, regex))
    return routes

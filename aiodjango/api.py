import asyncio
import inspect

from importlib import import_module

from django.conf import settings
from django.contrib.admindocs.views import extract_views_from_urlpatterns
from django.core.wsgi import get_wsgi_application

from aiohttp import web
from aiohttp_wsgi import WSGIHandler


def get_aio_application(wsgi=None):
    """Builds a aiohttp application wrapping around a Django WSGI server."""

    handler = WSGIHandler(wsgi or get_wsgi_application())
    app = web.Application()
    urlconf = import_module(settings.ROOT_URLCONF)
    view_functions = extract_views_from_urlpatterns(urlconf.urlpatterns)
    for (func, regex, namespace, name) in view_functions:
        if asyncio.iscoroutinefunction(func) or inspect.isgeneratorfunction(func):
            # Convert regex
            # TODO: Handle dynamic variables...
            path = regex.lstrip('^').rstrip('$')
            path = '/' + path if not path.startswith('/') else path
            # Add app route for co-routines
            app.router.add_route('*', path, func)
    app.router.add_route("*", "/{path_info:.*}", handler.handle_request, name='wsgi-app')
    return app

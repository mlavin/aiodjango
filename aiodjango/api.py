from django.conf import settings
from django.core.wsgi import get_wsgi_application

from aiohttp import web
from aiohttp_wsgi import WSGIHandler

from .routing import get_aio_routes


def get_aio_application(wsgi=None, include_static=False):
    """Builds a aiohttp application wrapping around a Django WSGI server."""

    handler = WSGIHandler(wsgi or get_wsgi_application())
    app = web.Application()
    for route in get_aio_routes():
        app.router.register_route(route)
    if include_static:
        app.router.add_static(settings.STATIC_URL, settings.STATIC_ROOT, name='static')
    app.router.add_route("*", "/{path_info:.*}", handler.handle_request, name='wsgi-app')
    return app

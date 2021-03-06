import tempfile

from unittest.mock import patch, Mock

from django.core.urlresolvers import reverse
from django.test import override_settings, SimpleTestCase

from .. import api
from ..test import async_test

# Empty set of URL patterns
urlpatterns = []


@override_settings(ROOT_URLCONF='aiodjango.tests.urls')
class GetApplicationTestCase(SimpleTestCase):
    """Building aihttp application around Django WSGI app."""

    def test_default_app(self):
        """Get default WSGI app."""
        with patch('aiodjango.api.get_wsgi_application') as mock_wsgi:
            api.get_aio_application()
            mock_wsgi.assert_called_with()

    def test_given_app(self):
        """WSGI app should be used if given."""
        with patch('aiodjango.api.get_wsgi_application') as mock_wsgi:
            api.get_aio_application(wsgi=Mock())
            self.assertFalse(mock_wsgi.called)

    def test_added_wsgi_route(self):
        """WSGI app should be added as a route to the aiohttp app."""
        with self.settings(ROOT_URLCONF=__name__):
            app = api.get_aio_application()
            self.assertEqual(len(app.router.routes()), 1)
            for route in app.router.routes():
                self.assertEqual(route.name, 'wsgi-app')

    def test_coroutine_routes(self):
        """Coroutines should be added as routes to the aiohttp application."""
        app = api.get_aio_application()
        self.assertEqual(len(app.router.routes()), 2)

    @async_test
    def test_resolve_wsgi(self):
        """Routing existing WSGI views should continue to work."""
        path = reverse('wsgi-ok')
        request = Mock(method='GET', raw_path=path)
        app = api.get_aio_application()
        match = yield from app.router.resolve(request)
        self.assertEqual(match.route.name, 'wsgi-app')

    @async_test
    def test_resolve_wsgi_fallback(self):
        """Any route not handled by a coroutine will fall back to the WSGI app."""
        path = '/this-path-does-not-exist/'
        request = Mock(method='GET', raw_path=path)
        app = api.get_aio_application()
        match = yield from app.router.resolve(request)
        self.assertEqual(match.route.name, 'wsgi-app')

    @async_test
    def test_coroutine_resolve_simple(self):
        """Simple path resolution should continue to work for added coroutines."""
        path = reverse('aiohttp-ok')
        request = Mock(method='GET', raw_path=path)
        app = api.get_aio_application()
        match = yield from app.router.resolve(request)
        self.assertEqual(match.route.name, 'aiohttp-ok')

    @async_test
    def test_static_route(self):
        """Optionally add the routing of static files."""
        with self.settings(STATIC_URL='/static/', STATIC_ROOT=tempfile.gettempdir()):
            app = api.get_aio_application(include_static=True)
            self.assertEqual(len(app.router.routes()), 3)
            request = Mock(method='GET', raw_path='/static/')
            match = yield from app.router.resolve(request)
            self.assertEqual(match.route.name, 'static')

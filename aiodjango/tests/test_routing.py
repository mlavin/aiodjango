import asyncio

from django.conf.urls import url
from django.http import HttpResponse
from django.test import override_settings, SimpleTestCase

from aiohttp.web import Response

from .. import routing


@asyncio.coroutine
def example(request):
    return Response(text='Ok')


@override_settings(ROOT_URLCONF='aiodjango.tests.urls')
class GetRoutesTestCase(SimpleTestCase):
    """Discover async routes including in Django URL patterns."""

    def test_use_root_conf(self):
        """If patterns aren't given then they are discovered from the ROOT_URLCONF."""
        routes = routing.get_aio_routes()
        self.assertEqual(len(routes), 1)

    def test_no_patterns(self):
        """Handle no patterns given."""
        routes = routing.get_aio_routes(patterns=[])
        self.assertEqual(len(routes), 0)

    def test_no_coroutines(self):
        """Handle no async callbacks given in the patterns."""
        patterns = (
            url(r'^$', lambda x: HttpResponse('Ok'), name='example'),
        )
        routes = routing.get_aio_routes(patterns=patterns)
        self.assertEqual(len(routes), 0)

    def test_simple_regex(self):
        """Handle regex with no variable matching."""
        patterns = (
            url(r'^/$', example, name='example'),
        )
        routes = routing.get_aio_routes(patterns=patterns)
        self.assertEqual(len(routes), 1)
        route = routes.pop()
        self.assertIsNotNone(route.match('/'))
        self.assertIsNone(route.match('/foo/'))

    def test_regex_grouping(self):
        """Handle regex with named variable groups."""
        patterns = (
            url(r'^/foo/(?P<foo>[0-9]+)/$', example, name='example'),
        )
        routes = routing.get_aio_routes(patterns=patterns)
        self.assertEqual(len(routes), 1)
        route = routes.pop()
        self.assertIsNotNone(route.match('/foo/123/'))
        self.assertIsNone(route.match('/foo/'))

    def test_leading_slash(self):
        """aiohttp expects a leading slash so it is automatically added."""
        patterns = (
            url(r'^$', example, name='example-no-slash'),
            url(r'^foo/(?P<foo>[0-9]+)/$', example, name='variable-no-slash'),
        )
        routes = routing.get_aio_routes(patterns=patterns)
        self.assertEqual(len(routes), 2)
        route = routes[0]
        self.assertIsNotNone(route.match('/'))
        route = routes[1]
        self.assertIsNotNone(route.match('/foo/123/'))

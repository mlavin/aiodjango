import asyncio

from django.http import HttpResponse
from aiohttp.web import Response


def hello(request):
    return HttpResponse('Hello')


@asyncio.coroutine
def world(request):
    return Response(body=b'World')

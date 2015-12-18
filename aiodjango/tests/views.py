import asyncio

from django.http import HttpResponse

from aiohttp.web import Response


def normal_ok(request):
    return HttpResponse('ok')


@asyncio.coroutine
def coroutine_ok(request):
    return Response(text='ok')

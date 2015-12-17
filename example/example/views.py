import asyncio

from django.shortcuts import render
from aiohttp.web import MsgType, WebSocketResponse


def index(request):
    return render(request, 'index.html')


@asyncio.coroutine
def socket(request):
    resp = WebSocketResponse()
    yield from resp.prepare(request)

    request.app.register_on_finish(resp.close)

    if 'sockets' not in request.app:
        request.app['sockets'] = []
    request.app['sockets'].append(resp)

    while True:
        msg = yield from resp.receive()
        if msg.tp == MsgType.text:
            for ws in request.app['sockets']:
                if ws is not resp:
                    ws.send_str(msg.data)
        else:
            break

    request.app['sockets'].remove(resp)
    return resp

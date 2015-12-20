import asyncio

from django.shortcuts import render

import aioamqp
from aiohttp.web import MsgType, WebSocketResponse


def index(request):
    return render(request, 'index.html')


@asyncio.coroutine
def socket(request):
    resp = WebSocketResponse()
    yield from resp.prepare(request)

    if 'amqp' not in request.app:
        transport, protocol = yield from aioamqp.connect()
        request.app['amqp'] = protocol

        @asyncio.coroutine
        def cleanup(app):
            yield from  protocol.close(timeout=1.0)
            transport.close()
        request.app.register_on_finish(cleanup)

    amqp = request.app['amqp']
    channel = yield from amqp.channel()
    exchange = yield from channel.exchange_declare(
        exchange_name='demo-room', type_name='fanout')
    result = yield from channel.queue_declare('', exclusive=True)
    yield from channel.queue_bind(result['queue'], 'demo-room', routing_key='')

    # Consume messages from the queue
    @asyncio.coroutine
    def message(channel, body, envelope, properties):
        if not resp.closed:
            resp.send_str(body.decode('utf-8'))

    yield from channel.basic_consume(message, queue_name=result['queue'])

    # Broadcast messages to the queue
    while True:
        msg = yield from resp.receive()
        if msg.tp == MsgType.text:
            yield from channel.publish(msg.data, exchange_name='demo-room', routing_key='')
        else:
            break
    # Client requested close
    yield from channel.close()
    return resp

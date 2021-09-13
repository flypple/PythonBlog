#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio, orm

from models import User
from aiohttp import web

async def testModel():
    await orm.create_pool(loop=eventLoop, user='root', password='password', db='PythonBlog')
    u = User(name='TestUser', email='test3@test.com', passwd='password', image='about:blank')
    await u.save()

def index(request):
    return web.Response(body=b'<h1>Hello!</h1>', content_type='html')

async def testRouter():
    app = web.Application()
    app.router.add_route('GET', '/', index)
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    print('app_runner.setup()')
    srv = await eventLoop.create_server(app_runner.server, 'localhost', 9000)
    print('server started at http://localhost:9000')
    return srv


if __name__ == '__main__':
    eventLoop = asyncio.get_event_loop()
    # eventLoop.run_until_complete(testModel())
    # eventLoop.close()
    eventLoop.run_until_complete(testRouter())
    eventLoop.run_forever()


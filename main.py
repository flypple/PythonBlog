#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: qinglin
@time: 2021/9/13
@desc:
"""

import asyncio
import json
import logging
import os
import time

import orm

from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from models import User
from web_core import add_routes, add_static
from config import configs
from handlers import cookie2user, COOKIE_NAME

logging.basicConfig(level=logging.INFO)

async def testModel():
    await orm.create_pool(loop=eventLoop, user='root', password='password', db='PythonBlog')
    u = User(name='TestUser', email='test3@test.com', passwd='password', image='about:blank')
    await u.save()


def index(request):
    return web.Response(body=b'<h1>Hello!</h1>', content_type='html')


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True),
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env

async def testRouter():
    app = web.Application()
    app.router.add_route('GET', '/', index)
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    print('app_runner.setup()')
    srv = await eventLoop.create_server(app_runner.server, 'localhost', 9000)
    print('server started at http://localhost:9000')
    return srv


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        # 原注释为等待睡眠0.3秒，目前不是很懂，难道在传进来的handler中等待的？
        return await handler(request)
    return logger


async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.info('set current user: %' % user.email)
                request.__user__ =  user
        if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__.admin):
            return web.HTTPFound('/signin')
        return await handler(request)
    return auth


async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return await handler(request)
    return parse_data


async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(status=r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(status=t, reason=str(m))
        # 默认
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response



def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def init_orm():
    await orm.create_pool(loop=eventLoop, **configs.db)


async def init_web():
    app = web.Application(loop=eventLoop, middlewares=[
        logger_factory, auth_factory, response_factory
    ])
    init_jinja2(app, filter=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')
    add_static(app)
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    print('app_runner.setup()')
    srv = await eventLoop.create_server(app_runner.server, 'localhost', 9000)
    print('server started at http://localhost:9000')
    return srv


async def init():
    await init_orm()
    return await init_web()


if __name__ == '__main__':
    eventLoop = asyncio.get_event_loop()
    # eventLoop.run_until_complete(testModel())
    # eventLoop.run_until_complete(testRouter())
    features = (init())
    eventLoop.run_until_complete(features)
    eventLoop.run_forever()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: qinglin
@time: 2021/9/14
@desc:
"""
from models import User
from web_core import get


@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
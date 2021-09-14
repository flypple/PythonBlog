#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: qinglin
@time: 2021/9/14
@desc: 
"""


class APIError(Exception):
    """
    基类APIError，error(必选参数), data(可选参数) and message(可选参数)
    """
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class APIValueError(APIError):
    """
    表示输入的值有出错或者无效 —— 数据指向了输入表单的错误字段
    """
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    """
    表示未找到资源 —— 数据指向了错误的资源名称
    """
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)


class APIPermissionError(APIError):
    """
    表示该对API没有访问权限
    """
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)
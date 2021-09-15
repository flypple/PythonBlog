#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: qinglin
@time: 2021/9/15
@desc: 配置文件
"""
import config_default


class ConfigDict(dict):
    """
    支持x.y风格访问的字典
    """

    def __init__(self, names=(), values=(), **kw):
        super(ConfigDict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s" % key)

    def __setattr__(self, key, value):
        self[key] = value


def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


def to_dict(a_dict):
    config_dict = ConfigDict()
    for k, v in a_dict.items():
        config_dict[k] = to_dict(v) if isinstance(v, dict) else v
    return config_dict


configs = config_default.configs


try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass

configs = to_dict(configs)
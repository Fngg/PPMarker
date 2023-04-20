# -*- coding: utf-8 -*-
def _init():  # 初始化
    global _global_dict
    _global_dict = {}


def set_value(key, value):
    """ 定义一个全局变量 """
    _global_dict[key] = value


def get_value(key, defValue=None):
    if _global_dict.__contains__(key):
        return _global_dict[key]
    else:
        set_value(key, defValue)
        return defValue
    # try:
    #     return _global_dict[key]
    # except KeyError:
    #     return defValue


def remove_value(key):
    if _global_dict.__contains__(key):
        return _global_dict.pop(key)
    else:
        return ""
# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general.const
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='get_attr')
def get_attr(value, arg=None):
    try:
        if isinstance(value, dict):
            return value.get(arg, None)
        else:
            return getattr(value, arg)
    except BaseException, ex:
        print str(ex)
        return None

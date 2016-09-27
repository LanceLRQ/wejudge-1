# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general.const
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='is_null')
def is_null(value, arg=None):
    try:
        if value is None:
            return True
        else:
            return False
    except BaseException,ex:
        print str(ex)
        return True

# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general.const
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='count_set')
def count_set(value, arg=None):
    try:
        if str(arg) == "model_set":
            return value.count()
        else:
            return len(value)

    except BaseException, ex:
        return 0

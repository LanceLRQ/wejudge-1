# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general.const
from django import template

__author__ = 'lancelrq'


register = template.Library()

week_list = ["一", "二","三","四","五","六","日"]

@register.filter(name='get_week')
def get_week(value, arg=None):
    try:
        return week_list[int(value) - 1]
    except BaseException, ex:
        return ""

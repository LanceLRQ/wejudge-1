# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
from django import template

__author__ = 'lancelrq'

register = template.Library()


@register.filter(name='full_time')
def full_time(value, arg=None):
    try:
        return kernel.GeneralTools.get_full_time_str(int(value), arg)
    except:
        return "00:00:00"

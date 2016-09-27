# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
from django import template

__author__ = 'lancelrq'

register = template.Library()


@register.filter(name='friendly_time')
def friendly_time(value, arg=None):
    try:
        return kernel.GeneralTools.friendly_time(int(value))
    except:
        return "NaN"

# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general.const
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='desc_status_flag')
def desc_status_flag(value, arg=None):
    try:
        return wejudge.kernel.general.const.JUDGE_STATUS_FLAG_DESC.get(int(value))
    except:
        return None

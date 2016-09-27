# -*- coding: utf-8 -*-
# coding:utf-8

from django import template
from wejudge.kernel.general import const
__author__ = 'lancelrq'

register = template.Library()


@register.filter(name='role_called')
def role_called(value, arg=None):
    try:
        return const.ACCOUNT_ROLE_CALLED[int(value)]
    except:
        return 'Unknow'


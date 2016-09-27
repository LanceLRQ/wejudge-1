# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general
from django import template
__author__ = 'lancelrq'

register = template.Library()


@register.filter(name='ratio')
def ratio(value, arg=None):
    return wejudge.kernel.general.GeneralTools.ratio(value, arg)

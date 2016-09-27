# coding:utf-8

import wejudge.kernel.general as kernel
from django import template
__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='language_called')
def language_called(value, arg=None):
    try:
        return kernel.const.LANGUAGE_DESCRIPTION.get(str(value), 'Unknow')
    except BaseException, ex:
        return 'Unknow'

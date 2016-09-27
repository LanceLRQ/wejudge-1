# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general.const
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='judge_lang_called')
def judge_lang_called(value, arg=None):
    try:
        return wejudge.kernel.general.const.LANGUAGE_DESCRIPTION.get(value)
    except:
        return 'Unknow'

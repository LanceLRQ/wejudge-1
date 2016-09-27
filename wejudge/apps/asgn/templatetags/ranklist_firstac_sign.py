# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='ranklist_firstac_sign')
def ranklist_firstac_sign(value, arg=None):
    try:
        sign = value.get("sign", "")
        if value.get("first_ac", 0) != 0:
            if sign in arg:
                return "bg-info"
            else:
                return "bg-success"
        else:
            if value.get("kda", 0) != 0:
                return "bg-danger"

    except BaseException, ex:
        return ''

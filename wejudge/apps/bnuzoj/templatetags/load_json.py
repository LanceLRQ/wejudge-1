# -*- coding: utf-8 -*-
# coding:utf-8

import json
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='load_json')
def load_json(value, arg=None):
    try:
        return json.loads(value)
    except BaseException,ex:
        return {}

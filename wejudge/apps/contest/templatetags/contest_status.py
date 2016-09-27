# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general
from django import template
import time
__author__ = 'lancelrq'

register = template.Library()


@register.filter(name='contest_status')
def contest_status(value, arg=None):
    try:
        s = int(value)
        e = int(arg)
        n = int(time.time())
        if n < s:
            return '<span class="label label-primary">未开始</span>'
        elif (n >= s) and (n <= e):
            return '<span class="label label-success">进行中</span>'
        else:
            return '<span class="label label-danger">已结束</span>'
    except:
        return '<span class="label label-default">Unknow</span>'

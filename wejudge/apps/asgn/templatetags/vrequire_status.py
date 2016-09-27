# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='vrequire_status')
def vrequire_status(value, arg=None):
    try:
        dat = value.get(arg, -2)
        if dat == -2:
            return '<a href="javascript:void(0)" data-id="%s" class="label label-info btn_visit_req">申请调课</a>' % arg
        elif dat == -1:
            return '<span class="label label-warning">调课申请中</span>'
        elif dat == 0:
            return '<span class="label label-danger">调课申请未通过</span>'
        elif dat == 1:
            return '<span class="label label-success">调课申请通过</span>'
        else:
            return '<span class="label label-default">无</span>'

    except BaseException, ex:
        return ''

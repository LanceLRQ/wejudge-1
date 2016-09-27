# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
from django import template

__author__ = 'lancelrq'


register = template.Library()


@register.filter(name='running_status')
def running_status(value, arg=None):
    try:
        dat = value.get(arg, -2)
        if dat[0] == -2:
            return '<span class="label label-default">无访问权限</span>'
        elif dat[0] == -1:
            return '<span class="label label-info">未开始 (%s后开始)</span>' % kernel.GeneralTools.get_full_time_str(dat[1], 'time')
        elif dat[0] == 0:
            return '<span class="label label-success">正在进行 (%s后截止)</span>' % kernel.GeneralTools.get_full_time_str(dat[1], 'time')
        elif dat[0] == 1:
            return '<span class="label label-danger">已结束 </span>'
        elif dat[0] == 2:
            if dat[1] == 0:
                return '<span class="label label-success">无待批改项目</span>'
            else:
                return '<span class="label label-warning">待批改作业(%s)</span>' % dat[1]
        elif dat[0] == 3:
            if dat[1] == 0:
                return '<span class="label label-success">课程助教：无作业可批改</span>'
            else:
                return '<span class="label label-warning">课程助教：待批改作业(%s)</span>' % dat[1]
        else:
            return '<span class="label label-success">未知</span>'

    except BaseException, ex:
        return ''

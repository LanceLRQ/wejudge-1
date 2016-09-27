# -*- coding: utf-8 -*-
# coding:utf-8

from django import template
import wejudge.kernel.general.const
__author__ = 'lancelrq'

register = template.Library()

@register.filter(name='show_diff_title')
def show_diff_title(value, arg=None):
    try:
        return wejudge.kernel.general.const.PROBLEM_DIFFICULTY.get(int(value), "未知")
    except:
        return "未知"

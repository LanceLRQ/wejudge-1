# -*- coding: utf-8 -*-
# coding:utf-8

from django import template
__author__ = 'lancelrq'

register = template.Library()


@register.filter(name='show_diff_star')
def show_diff_star(value, arg=None):
    try:
        stt = ""
        for i in range(int(value)):
            stt += "&starf;"
        return stt
    except:
        return ""

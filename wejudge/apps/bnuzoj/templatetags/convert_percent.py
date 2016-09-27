# -*- coding: utf-8 -*-
# coding:utf-8

from django import template
__author__ = 'lancelrq'

register = template.Library()


@register.filter(name='convert_percent')
def convert_percent(value, arg=None):
    return "%.2f%%" % (value * 100)
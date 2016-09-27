# -*- coding: utf-8 -*-
# coding:utf-8

from django import template
register = template.Library()

__author__ = 'lancelrq'


def cproblem_index(value, arg=None):
    try:
        v = int(value)
        outstr = ""
        while v > 0:
            outstr = chr(v % 26 + 64) + outstr
            v /= 26
        return outstr
    except:
        return "Unknow"

register.filter('cproblem_index', cproblem_index)
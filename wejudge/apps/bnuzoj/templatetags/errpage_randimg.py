# -*- coding: utf-8 -*-
# coding:utf-8

import random
from django import template

__author__ = 'lancelrq'


register = template.Library()

img_list = [
    "1.gif", "2.png", '3.jpg', '4.gif', '5.jpg', '6.jpg', '7.gif', '8.jpg', '9.jpg'
]


@register.filter(name='errpage_randimg')
def errpage_randimg(value, arg=None):
    return "/static/images/err_gif/%s" % img_list[random.randint(0, 8)]

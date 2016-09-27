# -*- coding: utf-8 -*-
# coding:utf-8
import json

__author__ = 'lancelrq'


class RESTStruct(object):
    """自定RESTful通信基础结构"""

    def __init__(self, flag, msg='', data=None, action=''):
        self.flag = flag
        self.msg = msg
        self.data = data
        self.action = action

    def dump(self):
        return json.dumps({
            'flag': self.flag,
            'msg': self.msg,
            'data': self.data,
            'action': self.action
        })
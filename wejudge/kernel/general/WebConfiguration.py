# -*- coding: utf-8 -*-
# coding:utf-8

import time
import wejudge.apps.bnuzoj.models as BnuzOJMdl

__author__ = 'lancelrq'


class WebConfiguration(object):
    """全站全局配置信息"""

    def __init__(self):
        """
        初始化配置信息
        :return:
        """
        """
        加载配置信息
        :return:
        """

        settings = BnuzOJMdl.Setting.objects.all()
        if settings.exists():
            self.__setting = settings[0]
        else:
            self.__setting = BnuzOJMdl.Setting()
            self.__setting.web_title = ""
            self.__setting.save()
            self.server_time = int(time.time())

    def __getattr__(self, item):
        """
        获取配置信息
        :param item: 属性名称
        :return:
        """
        if '__setting' in item:
            return object.__getattribute__(self, item)
        elif 'server_time' == str(item):
            return int(time.time())
        elif hasattr(self.__setting, item):
            return getattr(self.__setting, item)
        else:
            raise AttributeError("WebConfiguration attribute %s not found" % item)

    def __setattr__(self, key, value):
        """
        更改配置信息
        :param key: 属性名称
        :param value: 新值
        :return:
        """
        if '__setting' in key:
            return object.__setattr__(self, key, value)
        if hasattr(self.__setting, key):
            setattr(self.__setting, key, value)
        else:
            raise AttributeError("WebConfiguration attribute %s not found" % key)

    def save(self):
        """
        保存配置信息到数据库
        :return:
        """
        try:
            self.__setting.save()
        except BaseException, ex:
            raise RuntimeError("Cannot save WebConfiguration")


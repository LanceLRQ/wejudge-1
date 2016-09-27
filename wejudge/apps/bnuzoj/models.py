# -*- coding: utf-8 -*-
# coding:utf-8

from django.db import models

__author__ = 'lancelrq'


# 全站设置
class Setting(models.Model):

    # === 网站参数设置 ===

    web_title = models.CharField(max_length=255, blank=True, null=True)                 # 网站标题

    web_keyword = models.CharField(max_length=255, blank=True, null=True)               # 网站Keyword

    web_desc = models.CharField(max_length=255, blank=True, null=True)                  # 网站简介

    web_version = models.CharField(max_length=50, blank=True, null=True)                # 网站版本

    web_fixing = models.BooleanField(blank=False, null=False, default=False)            # 维护模式

    web_notice = models.TextField(blank=True, null=True, default="")                    # 网站公告

    web_stop_judging = models.BooleanField(blank=False, null=False, default=False)      # 暂停评测

    web_login_limit = models.BooleanField(blank=False, null=False, default=False)       # 登录限定（黑名单优先于白名单）

    web_login_white_list = models.TextField(blank=True, null=True, default='')          # 登录白名单(正则表达式，多组用换行隔开）

    web_login_black_list = models.TextField(blank=True, null=True, default='')          # 登录黑名单(正则表达式，多组用换行隔开）

    web_register = models.BooleanField(default=False)                                   # 是否开放网站注册

    web_pwd_equal_username = models.BooleanField(default=False)                         # 是否允许用户名和密码相同的用户登录

    # === smtp服务配置 ===

    smtp_server = models.CharField(max_length=50, blank=True, null=True)                # smtp服务器

    smtp_user = models.CharField(max_length=50, blank=True, null=True)                  # smtp用户名

    smtp_pwd = models.CharField(max_length=50, blank=True, null=True)                   # smtp密码

    smtp_mail_from = models.CharField(max_length=50, blank=True, null=True)             # smtp发件账户

    # === EDU ===

    year = models.SmallIntegerField(default=2015, null=False, blank=False)              # 当前学年度

    term = models.SmallIntegerField(default=1, null=False, blank=False)                 # 当前学期

    def __unicode__(self):
        if self.web_title is not None:
            return u"[%s] 网站配置信息" % self.web_title
        return u"网站配置信息"
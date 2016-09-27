# -*- coding: utf-8 -*-
# coding:utf-8

from __future__ import unicode_literals

from django.db import models
import wejudge.apps.account.models as AccountModel


SCOUP = (
    ('auth_base', 'Auth Login Only'),       # 仅登录
    ('auth_userinfo', 'Get UserInfo')       # 可以获取用户信息
)


# 授权的APP客户
class Client(models.Model):

    # 客户账号
    username = models.CharField(max_length=50, null=True, blank=True)
    # 客户密码
    password = models.CharField(max_length=100, null=True, blank=True)
    # 商家简介
    description = models.CharField(max_length=100, null=True, blank=True)
    # 客户显示名称
    appname = models.CharField(max_length=20, null=True, blank=True)
    # 客户商标
    avatar = models.CharField(max_length=100, null=True, blank=True)
    # APP_ID
    app_id = models.CharField(max_length=100, unique=True)
    # APP密钥
    app_secert = models.CharField(max_length=100, null=True, blank=True)
    # 允许的授权方式
    # grant_type = models.CharField(max_length=18, choices=[('authorization_code', 'Authorization code')])
    # 允许的应答方式
    # response_type = models.CharField(max_length=4, choices=[('code', 'Authorization code')])
    # AccessToken过期时间(s)
    at_expires_time = models.IntegerField(default=7200)
    # Refreshoken过期时间(s)
    # 使用RefreshToken后AccessToken的有效期将会以当前时间为准延后client.rf_rxpires_time个单位
    # 只能使用一次
    rt_expires_time = models.IntegerField(default=604800)
    # 允许访问的作用域
    # scopes = models.CharField(max_length=20, choices=SCOUP, default='auth_base')
    # 授权回调地址
    redirect_uris = models.TextField(default='')
    # 授权取消后回调地址
    cancel_redirect_uri = models.TextField(default='')

    def __unicode__(self):
        return 'name=%s;app_id=%s' % (self.appname, self.app_id)


class UserAllowClient(models.Model):
    # APP
    client = models.ForeignKey('Client')
    # 所属用户
    account = models.ForeignKey(AccountModel.User)
    # 是否允许该客户端进行访问
    is_allow = models.BooleanField(default=False)
    # OpenID
    open_id = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return 'client=(%s);account=(%s);is_allow=%s;open_id=%s' % (self.client, self.account, self.is_allow, self.open_id)


# 临时令牌存储(单个应用单个用户仅能存在一个code）
class AuthCode(models.Model):
    # APP
    client = models.ForeignKey('Client')
    # 所属用户
    account = models.ForeignKey(AccountModel.User, null=True, blank=True)
    # 允许访问的作用域
    scopes = models.CharField(max_length=20, choices=SCOUP, default='auth_base')
    # AccessToken
    code = models.CharField(max_length=100, unique=True)
    # 过期时间戳
    expires_at = models.IntegerField(default=0)

    def __unicode__(self):
        return 'client=(%s);account=(%s);expires_at=%s' % (self.client, self.account, self.expires_at)


# 令牌存储(单个应用单个用户仅能存在一个access_token）
class Tokens(models.Model):
    # APP
    client = models.ForeignKey('Client')
    # 所属用户
    account = models.ForeignKey(AccountModel.User, null=True, blank=True)
    # Open ID
    open_id = models.CharField(max_length=100, null=True, blank=True)
    # 允许访问的作用域
    scopes = models.CharField(max_length=20, choices=SCOUP, default='auth_base')
    # AccessToken
    access_token = models.CharField(max_length=100, unique=True)
    # RefreshToken
    refresh_token = models.CharField(max_length=100, unique=True)
    # AccessToken过期时间戳
    expires_at = models.IntegerField(default=0)

    def __unicode__(self):
        return 'client=(%s);account=(%s);expires_at=%s' % (self.client, self.account, self.expires_at)

"""
open_id 算法

SHA1(Client.appid + Account.user_id)

"""
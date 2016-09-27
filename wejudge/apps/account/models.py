# -*- coding: utf-8 -*-
# coding:utf-8


import math
from django.db import models

__author__ = 'lancelrq'


# 用户信息
class User(models.Model):

    # === 基本信息 ===

    id = models.CharField(max_length=50, primary_key=True)                                  # 用户ID（学号、工号、账号）

    password = models.CharField(max_length=100, blank=True, null=True)                      # 用户密码

    role = models.SmallIntegerField(blank=False, null=False, default=0)                     # 用户类型

    sex = models.SmallIntegerField(blank=False, null=False, default=-1)                     # 用户性别

    realname = models.CharField(max_length=50, blank=True, null=True)                       # 真实姓名

    nickname = models.CharField(max_length=50, blank=True, null=True)                       # 用户昵称

    headimg = models.CharField(max_length=50, blank=True, null=True)                        # 用户头像

    email = models.EmailField(blank=True, null=True)                                        # 用户邮箱

    motto = models.CharField(max_length=255, blank=True, null=True)                         # 个性签名

    create_time = models.IntegerField(blank=False, null=False, default=0)                   # 用户创建时间

    last_login_time = models.IntegerField(default=0)                                        # 最后一次登录的时间

    # === 安全设置 ===

    email_validated = models.BooleanField(blank=False, null=False, default=False)           # 邮箱是否认证

    email_findpwd_validated = models.CharField(max_length=100, blank=True, null=True)       # 邮箱验证用的token

    logined_token = models.CharField(max_length=100, blank=True, null=True)                 # 登录token

    logined_token_expire = models.IntegerField(blank=False, null=False, default=0)          # 登录token有效期

    login_pwd_retry_counter = models.SmallIntegerField(blank=False, null=False, default=5)  # 重试密码计数

    # === 代码提交计数 ===

    visited = models.IntegerField(blank=False, null=False, default=0)                       # 提交过多少题目

    solved = models.IntegerField(blank=False, null=False, default=0)                        # 解决了多少题目

    submissions = models.IntegerField(blank=False, null=False, default=0)                   # 提交代码的次数

    accepted = models.IntegerField(blank=False, null=False, default=0)                      # AC代码计数

    locked = models.BooleanField(blank=False, null=False, default=False)                    # 账号锁定（不能登录）

    # === 通用用户积分系统 ===

    point_solved = models.IntegerField(default=0)                                           # 积分：问题解决数量

    point_login = models.IntegerField(default=0)                                            # 积分：登录点数

    # === 用户特殊权限 ===

    spc_problem_publish = models.BooleanField(blank=False, null=False, default=False)       # 问题发布

    spc_problem_viewer = models.BooleanField(blank=False, null=False, default=False)        # 查看他人代码(包括判题机详情)

    # === 微信登陆部分 ===

    wc_access_token = models.CharField(max_length=255, blank=True, null=True)

    wc_expires_in = models.CharField(max_length=255, blank=True, null=True)

    wc_refresh_token = models.CharField(max_length=255, blank=True, null=True)

    wc_openid = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    wc_user_info = models.TextField(blank=True, null=True, default="")                      # WeChat用户信息

    # === 用户偏好设置 ===

    preference_language = models.CharField(max_length=10, default='gcc', blank=True, null=True)      # 默认语言

    preference_bgimg = models.CharField(max_length=255, default='', blank=True, null=True)           # OJ背景

    preference_problem_detail_mode = models.BooleanField(default=True)                              # 问题列表显示模式

    def __unicode__(self):
        return u'id = %s，%s，昵称：%s，真实姓名：%s，Email:%s' % (self.id, self.role, self.nickname, self.realname, self.email)

    def __getattr__(self, item):
        if item == 'level':
            # 逆推公式： L = sqrt (P)
            return int(math.floor(math.sqrt(self.point_total)))
        elif item == 'next_level_point':
            # 等级公式：下一级等级所需分数 P = L ^ 2
            nl = self.level + 1
            return int(math.pow(nl, 2))
        elif item == 'point_total':
            return self.point_login + self.point_solved
        elif item == 'next_level_ratio':
            if self.next_level_point == 0:
                return 0.0
            return (self.point_total * 1.0 / self.next_level_point) * 100.0
        else:
            return self.__getattribute__(item)


# 学生信息专用表
class Student(models.Model):

    account = models.ForeignKey("User")
    # 学号
    studentId = models.CharField(max_length=10, default="")
    # 教务密码
    studentPwd = models.CharField(max_length=200, default="")
    # 真实姓名
    studentName = models.CharField(max_length=20, default="")
    # 年级
    grade = models.SmallIntegerField(default=2014)
    # 性别
    sex = models.CharField(max_length=2, default="未知")
    # 行政班级
    className = models.CharField(max_length=20, default="")
    # 所属学院
    department = models.CharField(max_length=20, default="")
    # 所属专业
    major = models.CharField(max_length=20, default="")
    # 原始信息
    rawData = models.TextField(default="")

    def __unicode__(self):
        return u'id = %s，（%s），学号：%s，真实姓名：%s' % (self.id, self.account, self.studentId, self.studentName)

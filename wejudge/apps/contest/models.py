# -*- coding: utf-8 -*-
# coding:utf-8

from __future__ import unicode_literals
from django.db import models
import wejudge.apps.account.models as AppAccount
import wejudge.apps.problem.models as AppProblem

__author__ = 'lancelrq'


# 比赛
class Contest(models.Model):

    title = models.CharField(max_length=100, null=True, blank=True)                 # 比赛名称

    description = models.TextField(null=True, blank=True)                           # 比赛简介（页面内）

    start_time = models.IntegerField(default=0)                                     # 开始时间

    end_time = models.IntegerField(default=0)                                       # 结束时间

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)              # 发布者

    problemset = models.ManyToManyField("ContestProblems", blank=True)              # 题目集合

    referees = models.TextField(null=True, blank=True, default="")                  # 裁判

    pause = models.BooleanField(default=False)                                      # 暂停比赛(暂停提交）

    user_limit = models.TextField(null=True, blank=True, default="all")             # 参赛者权限（支持多条正则表达式匹配）

    lang = models.CharField(max_length=255, null=True, blank=True, default="all")   # 允许使用的语言(默认所有)

    judge_status = models.ManyToManyField(AppProblem.JudgeStatus, blank=True)       # 评测状态关联

    rank_list = models.TextField(null=True, blank=True, default="")                     # 排行榜缓存

    rank_list_cache_time = models.IntegerField(default=0)                               # 排行榜缓存刷新时间（无阻止）

    rank_list_1hr_stop = models.TextField(null=True, blank=True, default="")            # 排行榜缓存(1小时刷新）

    def __unicode__(self):
        return u"id = %d , 比赛名称：%s" % (self.id, self.title)


# 比赛题目设置
class ContestProblems(models.Model):

    index = models.IntegerField(default=0)                                              # 题目顺序

    problem = models.ForeignKey(AppProblem.Problem, null=True, blank=True)              # 题目关联

    accepted = models.IntegerField(default=0)                  # 通过题目数量

    submission = models.IntegerField(default=0)                # 提交题目数量

    lang = models.CharField(max_length=255, null=True, blank=True, default="inherit")   # 允许使用的语言(默认继承父节点)

    judge_style = models.IntegerField(default=0)               # 0：自动评测、1：半自动评测（评测结果可更改）、2：手动评测

    def __unicode__(self):
        return u"id = %s,  PID=%s" % (self.id, self.problem)


# 比赛题目解决情况
class ContestSolution(models.Model):

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)                      # 提交者

    contest = models.ForeignKey("Contest", null=True, blank=True)                           # 归属比赛

    problems = models.ForeignKey(AppProblem.Problem, null=True, blank=True)                 # 对应的的题目

    judge_status = models.ManyToManyField(AppProblem.JudgeStatus, blank=True)               # 提交状态（多个）

    submission = models.IntegerField(default=0)                                             # 提交计数器

    ignore = models.IntegerField(default=0)                                                 # 不计入错误的提交个数

    accepted = models.IntegerField(default=0)                                               # 通过计数器

    first_ac_time = models.IntegerField(default=-1)                                         # 第一次AC的时间

    def __unicode__(self):
        return "ID=%s, contestID=%s, userid=%s, pid=%s" % (self.id, self.contest.id, self.author.id, self.problems.id)


# 比赛问答系统
class FAQ(models.Model):

    contest = models.ForeignKey("Contest", null=True, blank=True)                   # 归属比赛

    is_notice = models.BooleanField(default=False)                                  # 提问类型（0：参赛者问，1：裁判发布）

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)              # 提问发起人

    subject = models.CharField(max_length=100, null=True, blank=True, default='')   # 提问主题(可以为空）

    content = models.TextField(null=True, blank=True, default='')                   # 提问内容

    create_time = models.IntegerField(default=0)                                    # 提问发起时间

    answer_referee = models.ForeignKey(AppAccount.User, blank=True, null=True, related_name="answer_referees")   # 回答提问的裁判

    answer_content = models.TextField(null=True, blank=True, default='')            # 回答内容

    answer_time = models.IntegerField(default=0)                                    # 回答时间

    is_private = models.BooleanField(default=True)                                  # 是否为私有问题（默认为‘是’）

    def __unicode__(self):
        return "msg[%d] = %s (by: %s)" % (self.id, self.subject, self.author.id)


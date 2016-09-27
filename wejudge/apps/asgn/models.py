# -*- coding: utf-8 -*-
# coding:utf-8

from django.db import models
import wejudge.apps.account.models as AppAccount
import wejudge.apps.education.models as AppEducation
import wejudge.apps.problem.models as AppProblem

__author__ = 'lancelrq'


# 作业数据表
class Asgn(models.Model):

    # === 基本信息 ===

    name = models.CharField(max_length=255, blank=True, null=True)                                  # 作业名称

    author = models.ForeignKey(AppAccount.User, null=True, blank=True, related_name='author')       # 作业发布者

    remark = models.TextField(null=True, blank=True)                                                # 作业描述

    course = models.ForeignKey(AppEducation.Course, null=True, blank=True)                          # 关联课程

    problemset = models.ManyToManyField('AsgnProblems', blank=True)                                 # 作业包含的题目

    create_time = models.IntegerField(blank=False, null=False, default=0)                           # 创建时间

    full_score = models.IntegerField(blank=False, null=False, default=0)                            # 给分上限

    lang = models.CharField(max_length=255, null=True, blank=True, default="all")                   # 允许使用的语言(默认所有)

    judge_status = models.ManyToManyField(AppProblem.JudgeStatus, blank=True)                       # 评测状态关联

    # arrangement = models.ManyToManyField(AppEducation.Arrangement, blank=True)                      # 教学班分组

    # arrangement_setting = models.TextField(null=False, blank=False, default="{}")                   # 教学班分组配置(json)

    access_control = models.ManyToManyField('AsgnAccessControl', blank=True)                        # 排课权限控制

    rank_list = models.TextField(null=True, blank=True)                                             # 排行榜信息缓存(json)

    rank_list_cache_time = models.IntegerField(blank=False, null=False, default=0)                  # 排行榜信息缓存时间

    black_list = models.ManyToManyField(AppAccount.User, blank=True, related_name='black_list')     # 黑名单

    def __unicode__(self):
        return "ID=%s, name=%s" % (self.id, self.name)


# 作业题目信息(包含设置)
class AsgnProblems(models.Model):

    problem = models.ForeignKey(AppProblem.Problem, null=True, blank=True)     # 题目关联

    accepted = models.IntegerField(blank=False, null=False, default=0)                  # 通过题目数量

    submission = models.IntegerField(blank=False, null=False, default=0)                # 提交题目数量

    require = models.BooleanField(default=False)                                        # 是否必做

    score = models.IntegerField(blank=False, null=False, default=0)                     # 评测机给分

    lang = models.CharField(max_length=255, null=True, blank=True, default="inherit")   # 允许使用的语言(默认继承父节点)

    def __unicode__(self):
        return u"id = %s,  PID=%s" % (self.id, self.problem)


# 作业访问权限控制
class AsgnAccessControl(models.Model):

    arrangement = models.ForeignKey(AppEducation.Arrangement, blank=True, null=True)        # 指向某个排课信息

    start_time = models.IntegerField(default=0)                                             # 开始时间

    end_time = models.IntegerField(default=0)                                               # 结束时间

    enabled = models.BooleanField(default=False)                                            # 是否启用

    def __unicode__(self):
        return u"id = %s,  arrangement = %s" % (self.id, self.arrangement)

# 作业访问权限请求（用于调课）
class AsgnVisitRequirement(models.Model):

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)                      # 提交者

    asgn = models.ForeignKey("Asgn", null=True, blank=True)                                 # 作业

    arrangement = models.ForeignKey(AppEducation.Arrangement, blank=True, null=True)        # 指向某个排课信息

    source_arrangement = models.ForeignKey(AppEducation.Arrangement, blank=True, null=True, related_name='source_arrangement')        # 原先的排课信息

    flag = models.SmallIntegerField(default=-1)                                              # 通过情况（0：未通过，1：通过）

    create_time = models.IntegerField(default=0)                                            # 请求创建时间

    proc_time = models.IntegerField(default=0)                                              # 通过时间


# 题目的解决情况
class Solution(models.Model):

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)                      # 提交者

    start_time = models.IntegerField(blank=False, null=False, default=0)                    # 第一次访问题目时间

    asgn = models.ForeignKey(Asgn, null=True, blank=True)                                   # 对应的作业

    problems = models.ForeignKey(AppProblem.Problem, null=True, blank=True)                 # 对应的的题目

    judge_status = models.ManyToManyField(AppProblem.JudgeStatus, blank=True)               # 提交状态（多个）

    submission = models.IntegerField(blank=False, null=False, default=0)                    # 提交计数器

    ignore = models.IntegerField(blank=False, null=False, default=0)                        # 不计入错误的提交个数

    accepted = models.IntegerField(blank=False, null=False, default=0)                      # 通过计数器

    first_ac_time = models.IntegerField(blank=False, null=False, default=-1)                # 第一次AC的时间

    def __unicode__(self):
        return "ID=%s, asgnid=%s, stuid=%s, pid=%s" % (self.id, self.asgn.id, self.author.id, self.problems.id)


# 实验报告信息表
class StuReport(models.Model):

    student = models.ForeignKey(AppAccount.User, null=True, blank=True)                 # 提交者

    asgn = models.ForeignKey('Asgn', null=True, blank=True)                             # 对应的作业

    judge_score = models.IntegerField(blank=False, null=False, default=0)               # 评测机得分

    finally_score = models.IntegerField(blank=False, null=False, default=0)             # 最终得分

    ac_counter = models.IntegerField(blank=False, null=False, default=0)                # 通过题目数量

    submission_counter = models.IntegerField(blank=False, null=False, default=0)        # 提交题目数量

    solved_counter = models.IntegerField(blank=False, null=False, default=0)            # 解决题目数量

    impression = models.TextField(blank=True, null=True)                                # 学生感想

    create_time = models.IntegerField(blank=False, null=False, default=0)               # 报告生成时间

    modify_time = models.IntegerField(blank=False, null=False, default=0)               # 报告最后修改时间

    teacher_check = models.BooleanField(default=False)                                  # 老师是否批阅？

    teacher_remark = models.TextField(null=True, blank=True)                            # 老师的批语

    def __unicode__(self):
        return "ID=%s, asgnid=%s, stuid=%s" % (self.id,self.asgn.id, self.student.id)


"""
分组鉴权机制:
->学生访问Asgn,系统查询排课表,进而查询出排课表,只要查到存在则返回True,否则返回False.如果Report表有记录了,则认为学生已经进入过作业,
  则权限自动打开!
排行榜"开始时间"判定:
->第一次打开作业时,Report报告记录自动生成,记录其生成时间,为开始做作业的时间.
教学班分组设置:
->由于每个人什么时候能访问作业是按教学班设置的时间计算的,如果要设置一些特殊的时间,则需要额外的配置信息,考虑到负载,不再使用新的表来记录.
自由授权机制:
->程序给定Signature,学生输入作业的signature数字后即可进入作业.由于进入作业后会产生Report记录,因此不再设置白名单.
->总体优先级为:Report记录(可删除) > 黑名单 > 教学班 > 自由鉴权码


教学班额外设置信息
存储内容:排课信息ID, 开始时间, 结束时间, 是否开启(默认开启, 如果不开启的话则视作该排课信息无效)
"""
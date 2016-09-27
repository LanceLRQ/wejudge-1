# -*- coding: utf-8 -*-
# coding:utf-8

from django.db import models
import wejudge.apps.account.models as AppAccount
import wejudge.apps.education.models as AppEducation

__author__ = 'lancelrq'


# 题目数据
class Problem(models.Model):

    # === 基础信息 ===

    title = models.CharField(max_length=255, blank=True, null=True)                 # 题目名称

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)              # 题目作者

    difficulty = models.SmallIntegerField(blank=False, null=False, default=0)       # 题目难度(0-5, 0表示未分级)

    classify = models.ForeignKey('ProblemClassify', blank=True, null=True)          # 题目所属分类

    # === 题目内容部分 ===

    description = models.TextField(null=True, blank=True)                           # 题目说明

    perview = models.CharField(max_length=255, blank=True, null=True)               # 题目说明精简版

    input = models.TextField(null=True, blank=True)                                 # 输入要求

    output = models.TextField(null=True, blank=True)                                # 输出要求

    sample_input = models.TextField(null=True, blank=True)                          # 输入样例

    sample_output = models.TextField(null=True, blank=True)                         # 输出样例

    hint = models.TextField(null=True, blank=True)                                  # 小贴士

    source = models.TextField(null=True, blank=True)                                # 题目来源

    demo_code = models.TextField(null=True, blank=True)                             # 示例代码

    test_data = models.ManyToManyField('TestData', blank=True)                      # 测试数据

    # === 评测选项 ===

    c_time_limit = models.IntegerField(blank=False, null=False, default=0)          # c/c++语言评测时间限制

    c_memory_limit = models.IntegerField(blank=False, null=False, default=0)        # c/c++语言评测内存限制

    java_time_limit = models.IntegerField(blank=False, null=False, default=0)       # java语言评测时间限制

    java_memory_limit = models.IntegerField(blank=False, null=False, default=0)     # java语言评测内存限制

    allow_predict = models.BooleanField(blank=False, null=False, default=False)     # 预评测选项开关(未启用）

    # === 题目选项 ===

    is_show = models.BooleanField(blank=False, null=False, default=False)           # 是否显示在题目列表

    create_time = models.IntegerField(blank=False, null=False, default=0)           # 题目发布时间

    update_time = models.IntegerField(blank=False, null=False, default=0)           # 题目更新时间

    is_private = models.BooleanField(blank=False, null=False, default=False)        # 私有模式(仅发布者可以查看)

    disable_edit_by_other = models.BooleanField(blank=False, null=False, default=False)      # 禁止他人修改

    pre_verify = models.ForeignKey(AppAccount.User, blank=True, null=True, default=None, related_name='pv_user')  # None为无须审核

    pause_judge = models.BooleanField(blank=False, null=False, default=True)      # 暂停评测

    # === 题目计数器缓存 ===

    total = models.IntegerField(blank=False, null=False, default=0)                             # 总计提交次数

    ac = models.IntegerField(blank=False, null=False, default=0)                                # AC次数

    def __unicode__(self):
        return u"%d. %s" % (self.id, self.title)


class TestData(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True, default='')      # 测试数据名称

    order = models.IntegerField(blank=True, null=True, default=0)                   # 测试数据顺序

    handle = models.CharField(max_length=255, blank=True, null=True, default='', db_index=True)    # 唯一标识符号

    update_time = models.IntegerField(blank=False, null=False, default=0)           # 更新时间

    available = models.BooleanField(blank=False, null=False, default=True)          # 测试数据可用

    visible = models.BooleanField(blank=False, null=False, default=True)            # 测试数据公开(仅对学生\一般用户有效)

    def dump_for_judge(self):
        return {
            "name": self.name,
            "handle": self.handle,
            "order": self.order,
            "available": self.available,
        }

    def __unicode__(self):
        return u"%s [%s]" % (self.name, self.handle)


# 课程分类信息
# 分类仅能被作者或者管理员编辑
class ProblemClassify(models.Model):

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)              # 分类作者

    title = models.CharField(max_length=255, blank=True, null=True)                 # 分类标题

    parent = models.ForeignKey('ProblemClassify', null=True, blank=True)            # 父分类节点

    def __unicode__(self):
        return u"%s (id = %d)" % (self.title, self.id)


# 评测状态详情
class JudgeStatus(models.Model):

    problem = models.ForeignKey('Problem', null=True, blank=True)                   # 对应题目

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)              # 提交者

    flag = models.SmallIntegerField(blank=False, null=False, default=-2)            # 评测状态

    lang = models.CharField(max_length=20, blank=True, null=True, db_index=True)    # 评测语言

    timestamp = models.IntegerField(blank=False, null=False, default=0)             # 提交时间

    exe_time = models.IntegerField(blank=False, null=False, default=0)              # 运行时间（毫秒）

    exe_mem = models.IntegerField(blank=False, null=False, default=0)               # 内存占用（KB）

    code_len = models.IntegerField(blank=False, null=False, default=0)              # 代码长度（字节）

    code_path = models.CharField(max_length=100, blank=True, null=True)             # 代码文件位置

    callback = models.TextField(blank=True, null=True)                              # 回调处理程序

    result = models.TextField(blank=True, null=True)                                # 评测结果

    def __unicode__(self):
        return u"id = %d" % self.id


# 评测队列
class JudgeQueue(models.Model):

    judge_status = models.ForeignKey('JudgeStatus', blank=True, null=True)                    # 评测状态

    queue_status = models.SmallIntegerField(blank=False, null=False, default=0)               # 队列处理情况

    def __unicode__(self):
        return u"id = %d, judge_status_id = %d" % (self.id, self.judge_status.id)


# 题目访问计数器缓存
class ProblemVisited(models.Model):

    author = models.ForeignKey(AppAccount.User, null=True, blank=True)                          # 提交者

    problem = models.ForeignKey('Problem', blank=False, null=False)                             # 对应的问题

    submissions = models.IntegerField(blank=False, null=False, default=0)                       # 提交代码的次数

    accepted = models.IntegerField(blank=False, null=False, default=0)                          # 代码通过的次数


# 测试数据生成器队列
class TdmakerQueue(models.Model):

    author = models.ForeignKey(AppAccount.User, blank=True, null=True)                              # 提交者

    problem = models.ForeignKey('Problem', blank=True, null=True)                                   # 对应的问题

    queue_status = models.SmallIntegerField(blank=False, null=False, default=0)                     # 队列处理情况

    flag = models.SmallIntegerField(blank=False, null=False, default=0)                             # 运行情况

    memused = models.IntegerField(blank=False, null=False, default=0)                               # 运行情况 - 内存消耗

    timeused = models.IntegerField(blank=False, null=False, default=0)                              # 运行情况 - 时间消耗

    lang = models.CharField(max_length=20, blank=True, null=True)                                   # 代码语言

    def __unicode__(self):
        return u"id = %d, problem_id = %d" % (self.id, self.problem.id)
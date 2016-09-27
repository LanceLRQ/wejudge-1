# -*- coding: utf-8 -*-
# coding:utf-8

from django.db import models
import wejudge.apps.account.models as AppAccount

__author__ = 'lancelrq'


# 排课信息
class Arrangement(models.Model):

    parent_course = models.ForeignKey("Course", blank=True, null=True, related_name="parent_course")    # 所属课程

    signature = models.CharField(max_length=50, default='', null=True, blank=True)  # 操作标识符(用于选课)

    day_of_week = models.IntegerField(default=0, null=False, blank=False)           # 周几

    start_week = models.IntegerField(default=0, null=False, blank=False)            # 开始周

    end_week = models.IntegerField(default=0, null=False, blank=False)              # 结束周

    odd_even = models.IntegerField(default=0, null=False, blank=False)              # 单双周

    start_section = models.IntegerField(default=0, null=False, blank=False)         # 开始节

    end_section = models.IntegerField(default=0, null=False, blank=False)           # 结束节

    start_time = models.IntegerField(blank=True, null=True, default=0)              # 开始时间(24小时)

    end_time = models.IntegerField(blank=True, null=True, default=0)                # 结束时间(24小时)

    teacher = models.ForeignKey(AppAccount.User, null=True, blank=True, related_name="arrangement_teacher")    # 教师信息

    students = models.ManyToManyField(AppAccount.User, blank=True, related_name="arrangement_students")        # 学生信息(选课信息)

    def __getattr__(self, item):
        if item == 'toString':
            return self.toString()
        else:
            return self.__getattribute__(item)

    def toString(self):
        if self.odd_even == 1:
            odd = "(单周)"
        elif self.odd_even == 2:
            odd = "(双周)"
        else:
            odd = ""
        return u"%s周%d 第%d-%d节(%d-%d周)" % (
            odd, self.day_of_week, self.start_section, self.end_section,self.start_week, self.end_week
        )

    def __unicode__(self):
        if self.teacher is not None:
            tname = self.teacher.realname
        else:
            tname = ""
        return u"[%s]%s; %s" % (self.id, self.toString(), u"(任课：%s)" % tname)


# 课程表
class Course(models.Model):

    year = models.SmallIntegerField(default=2015, null=False, blank=False)          # 学年度,如果为2016则视作2015-2016年度

    term = models.SmallIntegerField(default=1, null=False, blank=False)             # 学期

    name = models.CharField(max_length=255, blank=True, null=True)                  # 课程名称

    arrangements = models.ManyToManyField('Arrangement', blank=True)                # 课程排课信息

    department = models.ForeignKey('EduDepartment', null=True, blank=True)          # 归属学院

    teacher = models.ForeignKey(AppAccount.User, blank=True, null=True, related_name="course_teacher")    # 任课教师列表

    assistants = models.ManyToManyField(AppAccount.User, blank=True, related_name="course_assistants")    # 助教名单

    repositories = models.ManyToManyField('Repository', blank=True)                 # 教学资源仓库列表

    def __unicode__(self):
        return u"%s - %s" % (self.id, self.name)


# 学院表
class EduDepartment(models.Model):

    id = models.CharField(max_length=50, primary_key=True)                           # 学院ID

    name = models.CharField(max_length=50, blank=True, null=True)                    # 学院名称

    def __unicode__(self):
        return u"%s - %s" % (self.id, self.name)


# 专业表
class EduMajor(models.Model):

    # 专业代号
    id = models.CharField(max_length=4, primary_key=True)
    # 专业短代号
    short_id = models.CharField(max_length=2)
    # 归属学院
    department = models.ForeignKey('EduDepartment', blank=True, null=True)
    # 专业名称
    name = models.CharField(max_length=50)



# 课程消息
class CourseMessage(models.Model):

    course = models.ForeignKey('Course', blank=True, null=True)                             # 课程信息

    title = models.CharField(max_length=255, blank=True, null=True)                         # 课程消息标题

    content = models.TextField(null=True, blank=True)                                       # 消息内容

    time = models.IntegerField(blank=False, null=False, default=0)                          # 发布时间

    deadline = models.IntegerField(blank=False, null=False, default=0)                      # 失效时间

    def __unicode__(self):
        return u'id = %d, course = %s, title = %s' % (self.id, self.course, self.title)


# 教学资源仓库
class Repository(models.Model):

    author = models.ForeignKey(AppAccount.User, blank=True, null=True)                      # 拥有者

    title = models.CharField(max_length=255, blank=True, null=True)                         # 仓库名称

    handle = models.CharField(max_length=255, null=True, blank=True, db_index=True)         # 仓库识别号

    max_size = models.IntegerField(blank=False, null=False, default=1073741824)             # 仓库最大容量(默认1G，字节)

    cur_size = models.IntegerField(blank=False, null=False, default=0)                      # 仓库当前容量(字节)

    def __unicode__(self):
        return u'Repository: id = %d, author = %s, title = %s' % (self.id, self.author.nickname, self.title)


"""
选课规则:
1. 自主导入:学生打开教学系统页面, 系统根据当前学期展示可以选择的所有课程, 学生点击课程后查看排课信息进行选取
   每个排课记录都有一个唯一的signature, 学生选择排课后, 输入老师展示出的该节课的signature即可进行选择
2. 教师导入:教师通过指定格式xls文件进行导入, 按排课记录依次导入, 学生会自动添加绑定到该课程.

注意:教师可以管理排课信息中所有学生的选课情况,可以将其踢出等操作.教师还可以自己创建排课信息.
"""
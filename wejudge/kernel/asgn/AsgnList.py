# -*- coding: utf-8 -*-
# coding:utf-8

import time
import django.core.urlresolvers
import wejudge.kernel.general as kernel
import wejudge.kernel.education as EduKernel
import wejudge.apps.asgn.models as AsgnModel
import AsgnProvider as Provider

__author__ = 'lancelrq'


class AsgnList(EduKernel.EduCenterProvider, Provider.AsgnProvider):

    def __init__(self, request):
        EduKernel.EduCenterProvider.__init__(self, request)
        self._navbar_action = 'asgn'

    def _get_view_term(self):
        """
        @override 获取当前查看的学期
        :return:
        """
        year = self._request.session.get('asgn_viewer_year', self._config.year)
        term = self._request.session.get('asgn_viewer_term', self._config.term)
        not_now_term = False
        if year != self._config.year or term != self._config.term:
            not_now_term = True

        return {
            'year': year,
            'term': term,
            'not_now_term': not_now_term
        }


    def index(self, course_id=None):

        if not self._check_login():
            return

        if self._user_session.user_role == 0:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_USER_ROLE_NO_USE_FUNC
            return

        view_term = self._get_view_term()  # 从Session中获取当前查看的学期

        choose_year = self._request.GET.get('year', view_term.get('year', self._config.year))
        choose_term = self._request.GET.get('term', view_term.get('term', self._config.year))
        try:
            choose_year = int(choose_year)
            choose_term = int(choose_term)
            self._request.session['asgn_viewer_year'] = choose_year
            self._request.session['asgn_viewer_term'] = choose_term
        except Exception, ex:
            self._request.session['asgn_viewer_year'] = self._config.year
            self._request.session['asgn_viewer_term'] = self._config.term

        view_term = self._get_view_term()  # 从Session中获取当前查看的学期

        course_list = self._get_course_choosing(view_term)  # 获取当前用户的选课信息

        if course_id is None and len(course_list) > 0:
            self._request.session['asgn_viewer_year'] = course_list[0].year
            self._request.session['asgn_viewer_term'] = course_list[0].term
            view_term = self._get_view_term()  # 从Session中获取当前查看的学期
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = django.core.urlresolvers.reverse("asgn_index", args=(course_list[0].id,))
            return

        course = self._get_course_by_id(course_id)

        self._template_file = "asgn/index.html"

        if course is not None:
            asgn_list = course.asgn_set.all()       # 获取当前学期的作业信息
            self._context = {
                'view_term': view_term,
                'course_list': course_list,
                'now_course': course,
                'asgn_list': asgn_list,
                'running_status':  self._get_asgn_running_status(asgn_list),
                'visit_require': self._get_asgn_visit_require_status(asgn_list),
                'message_list': self._get_course_message_top_list(course),
                'asgn_score': self._get_asgn_score(asgn_list),
                "year_terms": kernel.GeneralTools.get_year_terms()
            }
        else:
            self._context = {
                'view_term': view_term,
                'course_list': course_list,
                'now_course': course,
                "year_terms": kernel.GeneralTools.get_year_terms()
            }

    def score_counter(self, course_id=None):
        # 成绩统计模块
        if not self._check_login():
            return

        if self._user_session.user_role not in [2, 99]:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_USER_ROLE_NO_USE_FUNC
            return

        view_term = self._get_view_term()                       # 获取当前学期
        course_list = self._get_course_choosing(view_term)      # 获取当前用户选课记录

        if course_id is None and len(course_list) > 0:
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = django.core.urlresolvers.reverse("asgn_index", args=(course_list[0].id,))
            return

        course = self._get_course_by_id(course_id)
        if course is None:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_EDU_COURSE_NOT_FOUND
            return

        asgn_list = course.asgn_set.all()       # 获取当前学期的作业信息
        asgn_list_count = asgn_list.count()

        self._template_file = "asgn/counter.html"

        self._context = {
            'view_term': view_term,
            'course_list': course_list,
            'now_course': course,
            'asgn_list': asgn_list,
            'asgn_count_avg': (1.0 / asgn_list_count) * 100 if asgn_list_count > 0 else 0
        }


    def visit_req(self, asgn_id=None):
        """
        学生调课操作页面
        :param asgn_id:
        :return:
        """
        if not self._check_login(True, True):
            return

        if self._user_session.user_role != 1:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "非学生不能使用这个功能"
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "未找到作业"
            return

        if self._is_course_assistants(asgn.course):
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "助教不能使用这个功能"
            return

        self._template_file = "asgn/visit_req.html"
        self._context = {
            'asgn': asgn,
            'arrangements': asgn.course.arrangements.all()
        }

    def save_visit_req(self, asgn_id=None):
        """
        学生调课操作保存接口
        :param asgn_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        if self._user_session.user_role != 1:
            self._result = kernel.RESTStruct(False, "非学生不能使用这个功能")
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._result = kernel.RESTStruct(False, "未找到作业")
            return

        if self._is_course_assistants(asgn.course):
            self._result = kernel.RESTStruct(False, "助教不能使用这个功能")
            return

        id = self._request.POST.get('arrangement', '0')
        arrangement = asgn.access_control.filter(arrangement__id=id)
        if not arrangement.exists():
            self._result = kernel.RESTStruct(False, "未找到可用的排课信息")
            return
        arrangement = arrangement[0].arrangement

        vr = AsgnModel.AsgnVisitRequirement.objects.filter(asgn=asgn, author=self._user_session.entity)
        if vr.exists():
            self._result = kernel.RESTStruct(False, "当前作业你已经使用过调课申请了，请等待结果，如果有错请联系老师处理")
            return

        old_arr = None
        old_arrangement_list = asgn.course.arrangements.all()
        for old_arrangement in old_arrangement_list:
            stus = old_arrangement.students.filter(id=self._user_session.user.id)
            if stus.exists():
                old_arr = old_arrangement
                break

        vr = AsgnModel.AsgnVisitRequirement()
        vr.asgn = asgn
        vr.author = self._user_session.entity
        vr.create_time = int(time.time())
        vr.flag = -1
        vr.source_arrangement = old_arr
        vr.arrangement = arrangement
        vr.save()

        self._result = kernel.RESTStruct(True)

    def _get_asgn_running_status(self, asgn_list):
        """
        获取作业的运行状态信息
        :return:
        """
        asgn_running_status = {}
        for asgn in asgn_list:
            asgn_running_status[asgn.id] = self._check_asgn_permission(asgn)

        return asgn_running_status

    def _get_asgn_score(self, asgn_list):
        """
        获取作业的批改情况
        :return:
        """
        user = self._user_session.user
        if user is None:
            return None

        asgn_score = {}
        for asgn in asgn_list:
            rep = AsgnModel.StuReport.objects.filter(asgn=asgn, student=user)
            if rep.exists():
                rep = rep[0]
                if rep.teacher_check:
                    asgn_score[asgn.id] = rep.finally_score

        return asgn_score

    def _get_asgn_visit_require_status(self, asgn_list):
        """
        获取作业的学生调课状态信息
        :return:
        """
        req_status = {}
        for asgn in asgn_list:
            if self._user_session.user_role != 1:
                req_status[asgn.id] = -3
                continue
            reqs = AsgnModel.AsgnVisitRequirement.objects.filter(asgn=asgn, author=self._user_session.entity)
            flag = -2
            if reqs.exists():
                flag = reqs[0].flag
            req_status[asgn.id] = flag

        return req_status
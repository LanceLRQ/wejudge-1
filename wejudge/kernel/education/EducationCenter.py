# -*- coding: utf-8 -*-
# coding:utf-8
import wejudge.apps.education.models as EduModel
import django.core.urlresolvers
import wejudge.kernel.general as kernel
import EduCenterProvider as ECP
import datetime
__author__ = 'lancelrq'


class EducationCenter(ECP.EduCenterProvider):

    def __init__(self, request):
        ECP.EduCenterProvider.__init__(self, request)
        self._navbar_action = 'education'

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
            self._request.session['edu_viewer_year'] = choose_year
            self._request.session['edu_viewer_term'] = choose_term
        except Exception,ex:
            self._request.session['edu_viewer_year'] = self._config.year
            self._request.session['edu_viewer_term'] = self._config.term

        view_term = self._get_view_term()                           # 从Session中获取当前查看的学期
        course_list = self._get_course_choosing(view_term)          # 获取当前用户的选课信息

        if course_id is None and course_list is not None and len(course_list) > 0:
            self._request.session['edu_viewer_year'] = course_list[0].year
            self._request.session['edu_viewer_term'] = course_list[0].term
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = django.core.urlresolvers.reverse("education_index", args=(course_list[0].id,))
            return

        course = self._get_course_by_id(course_id)

        self._template_file = "education/home.html"
        self._context = {
            'view_term': view_term,
            'course_list': course_list,
            "course": course,
            "year_terms": kernel.GeneralTools.get_year_terms()
        }

    def course_info(self, course_id):
        """读取课程信息"""
        if not self._check_login(True, True):
            return
        course = self._get_course_by_id(course_id)                                   # 获取当前查看的课程
        if course is None:
            return
        self._template_file = "education/module/course_info.html"
        students = []
        for arr in course.arrangements.all():
            tmp_list = []
            for stu in arr.students.all():
                tmp_list.append(stu)
            students.append({
                "name": arr.toString(),
                "students": tmp_list
            })

        my_arr = course.arrangements.filter(students=self._user_session.user, parent_course=course)

        self._context = {
            'now_course': course,
            'now_course_students': students,
            'now_course_assistants': course.assistants.all() if course is not None else None,
            'my_arrangement': my_arr
        }

    def course_message(self, course_id):
        """课程通知"""
        if not self._check_login(True, True):
            return
        course = self._get_course_by_id(course_id)                                   # 获取当前查看的课程
        if course is None:
            return
        messages = EduModel.CourseMessage.objects.filter(course=course).order_by("-id")
        self._template_file = "education/module/course_message.html"
        self._context = {
            'course': course,
            'messages': messages
        }

    def course_message_detail(self, course_id, message_id):
        """课程通知详情"""
        if not self._check_login(True, True):
            return
        course = self._get_course_by_id(course_id)                                   # 获取当前查看的课程
        if course is None:
            return
        messages = EduModel.CourseMessage.objects.filter(course=course, id=message_id)
        if not messages.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "未找到课程通知，返回列表请刷新"
            return

        self._template_file = "education/module/course_message_detail.html"
        self._context = {
            'course': course,
            'message': messages[0]
        }

    def course_choosing(self, course_id=None):
        """选课页面"""
        if not self._check_login(True, True):
            return
        course_list = EduModel.Course.objects.filter(year=self._config.year, term=self._config.term)
        if course_id is not None:
            course = self._get_course_by_id(course_id)                                   # 获取当前查看的课程
            if course is None:
                self._action = kernel.const.VIEW_ACTION_DEFAULT
                self._context = "未找到课程"
                return
            else:
                arrangement = course.arrangements.all()
        else:
            arrangement = None
        self._template_file = "education/module/course_choosing.html"
        self._context = {
            'course_id': int(course_id) if course_id is not None else None,
            'course_list': course_list,
            'arrangements': arrangement
        }

    def save_course_choosing(self):
        """保存选课信息"""
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_role != 1:
            self._result = kernel.RESTStruct(False, '非学生账户不能选课')
            return
        course_id = self._request.POST.get('course', '0')
        arrangement_id = self._request.POST.get('arrangement', '0')
        sign = self._request.POST.get('sign', '')
        course = self._get_course_by_id(course_id)                                   # 获取当前查看的课程
        if course is None:
            self._result = kernel.RESTStruct(False, '未找到课程')
            return
        arr = course.arrangements.filter(id=arrangement_id)
        if not arr.exists():
            self._result = kernel.RESTStruct(False, '未找到排课信息')
            return
        arr = arr[0]
        if arr.students.filter(id=self._user_session.user_id).exists():
            self._result = kernel.RESTStruct(False, '你已经选过了当前的课程')
            return
        if self._check_signature(arr.signature, sign):
            arr.students.add(self._user_session.entity)
            self._result = kernel.RESTStruct(True)
        else:
            self._result = kernel.RESTStruct(False, '选课授权码错误或过期')

    def remove_arrangement(self, course_id, arrid):
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_role != 1:
            self._result = kernel.RESTStruct(False, '非学生账户不能执行该操作')
            return
        course = self._get_course_by_id(course_id)
        if course is None:
            self._result = kernel.RESTStruct(False, '未找到课程')
            return
        arr = course.arrangements.filter(id=arrid)
        if not arr.exists():
            self._result = kernel.RESTStruct(False, '未找到排课信息')
            return
        arr = arr[0]
        if not arr.students.filter(id=self._user_session.user_id).exists():
            self._result = kernel.RESTStruct(False, '您没有选择此排课')
            return
        arr.students.remove(self._user_session.entity)
        self._result = kernel.RESTStruct(True)

    def resource_repositories(self, course_id):
        """教学资料仓库"""
        if not self._check_login(True, True):
            return
        course = self._get_course_by_id(course_id)                                   # 获取当前查看的课程
        if course is None:
            return
        course_used_repository = []
        if self._user_session.user_role >= 2:
            repo_list = EduModel.Repository.objects.filter(author=self._user_session.entity).all()
            repo_list2 = course.repositories.all()
            for repo in repo_list2:
                course_used_repository.append(repo.handle)
        else:
            repo_list = course.repositories.all()
        self._template_file = "education/module/resource_repositories.html"
        self._context = {
            'course': course,
            'repositories': repo_list,
            'course_used_repository': course_used_repository
        }
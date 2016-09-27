# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'
import random
import time
import wejudge.kernel.general as kernel
import wejudge.apps.education.models as EduModel


class EduCenterProvider(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'education'

    def _get_course_by_id(self, cid):
        """
        获取课程信息
        :param cid:
        :return:
        """
        if cid is None or cid.strip() == '':
            return None
        c = EduModel.Course.objects.filter(id=cid)
        if c.exists():
            return c[0]
        return None

    def _get_course_choosing(self, view_term):
        """
        获取某个学期的选课记录
        :param view_term: 学年学期
        :return:
        """

        year = view_term.get('year')
        term = view_term.get('term')

        if self._user_session.user_role in [3, 99]:
            return EduModel.Course.objects.filter(year=year, term=term).order_by('-id')
        elif self._user_session.user_role == 2:
            return EduModel.Course.objects.filter(year=year, term=term, teacher=self._user_session.entity).order_by('-id')
        elif self._user_session.user_role == 1:
            course_list = []
            arrs = self._user_session.user.arrangement_students.filter(parent_course__year=year, parent_course__term=term)
            for arr in arrs:
                course_list.append(arr.parent_course)
            courses = self._user_session.user.course_assistants.filter(year=year, term=term)
            for course in courses:
                course_list.append(course)
            return list(set(course_list))
        else:
            return None

    def _is_course_assistants(self, course):
        """
        检测当前用户是否为当前课程的助教
        :param course:
        :return:
        """
        if course.assistants.filter(id=self._user_session.user_id).exists():
            return True
        else:
            return False

    def _get_view_term(self):
        """
        获取当前查看的学期
        :return:
        """
        year = self._request.session.get('edu_viewer_year', self._config.year)
        term = self._request.session.get('edu_viewer_term', self._config.term)
        not_now_term = False
        if year != self._config.year or term != self._config.term:
            not_now_term = True

        return {
            'year': year,
            'term': term,
            'not_now_term': not_now_term
        }

    def _get_course_message_top_list(self, course):
        """
        返回当前没有超过DeadLine的课程消息
        :param course:
        :return:
        """
        message = EduModel.CourseMessage.objects.filter(course=course, deadline__gte=int(time.time()))
        if message.exists():
            return message
        else:
            return None

    def _create_signature(self):
        """
        获取一个新的授权码
        :return:
        """
        expire = int(time.time())
        code = random.randint(0, expire)
        return "%04d|%s" % (random.randint(code, expire) % 9000 + 1000, expire + 604800)

    def _get_signature(self, raw_signature):
        """
        获取授权码
        :param signature: 源授权码信息
        :return:
        """
        if raw_signature is None or raw_signature.strip() == '':
            return self._create_signature()
        else:
            signature = raw_signature.split("|")
            if len(signature) != 2:
                return self._create_signature()
            else:
                try:
                    sign = str(signature[0])
                    expire = int(signature[1])
                    if sign.strip() == '':
                        return self._create_signature()
                    if expire < int(time.time()):
                        return self._create_signature()
                    return raw_signature
                except:
                    return self._create_signature()

    def _check_signature(self, signature, vaild_txt):
        """
        选课授权码校验(时长为604800秒内有效）
        :param signature: 数据库内存储的授权码信息
        :param vaild_txt: 用户输入的信息
        :return:
        """
        if signature is None or signature.strip() == '':
            return False
        signature = signature.split("|")
        if len(signature) != 2:
            return False
        try:
            sign = str(signature[0])
            expire = int(signature[1])
            if sign.strip() == '':
                return False
            if expire < int(time.time()):
                return False
            if vaild_txt is None or str(vaild_txt) != sign:
                return False
            return True
        except:
            return False
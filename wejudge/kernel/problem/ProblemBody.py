# -*- coding: utf-8 -*-
# coding:utf-8
import time
import uuid
import hashlib
import wejudge.kernel.general as kernel
import wejudge.apps.problem.models as ProblemMdl
from django.core.urlresolvers import reverse
__author__ = 'lancelrq'


class ProblemBody(kernel.ViewerFramework):
    """问题展示"""

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'problem'

    # ===== Public =====

    def show_problem(self, pid, show_all=False):
        """
        题目展示（View）
        :param pid: 问题ID
        :param show_all: 强制显示
        :return:
        """
        # if not self._user_session.is_logined():
        #     self._action = kernel.const.VIEW_ACTION_LOGIN_REQUEST
        #     return
        if show_all:
            problem = ProblemBodyQuery.get_problem_detail(pid)
        else:
            if self._user_session.is_logined() and self._user_session.user_role >= 2:
                problem = ProblemBodyQuery.get_problem_detail(pid)
            else:
                problem = ProblemBodyQuery.get_problem_detail(pid, False)
            if problem is None:
                self._context = kernel.error_const.ERROR_PROBLEM_NOT_FOUND      # 未找到问题
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                return False
            if problem.is_private and (not self._user_session.is_logined() or (self._user_session.user_role != 99 and self._user_session.user_id != problem.author.id)):
                self._context = kernel.error_const.ERROR_PROBLEM_NOT_FOUND      # 禁止访问
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                return False
        self._context = {
            'problem': problem,
            'language_provider': kernel.const.LANGUAGE_PROVIDE
        }
        self._template_file = "problem/problem/view.html"
        return True

    def save_submission(self, pid):
        """
        保存提交（View）
        :param pid: 问题ID
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._user_session.is_logined():
            self._action = kernel.const.VIEW_ACTION_LOGIN_REQUEST
            self._content_type = kernel.const.VIEW_CONTENT_TYPE_JSON
            return
        else:
            result = self._save_submission(pid)
            if result.flag is True:
                result.data = result.data.id
            else:
                result.data = None
            self._result = result
            return

    def get_judge_history(self, pid):
        self._action = kernel.const.VIEW_ACTION_JSON
        p = ProblemBodyQuery.get_problem_detail(pid)
        if p is not None:
            flag_data = [
                {'y': p.ac, 'color': '#8BC34A', "url": reverse("problem_judge_status") + "?flag=0"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=1).count(), 'color': '#FFEB3B', "url": reverse("problem_judge_status") + "?flag=1"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=2).count(), 'color': '#FF9800', "url": reverse("problem_judge_status") + "?flag=2"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=3).count(), 'color': '#9C27B0', "url": reverse("problem_judge_status") + "?flag=3"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=4).count(), 'color': '#F44336', "url": reverse("problem_judge_status") + "?flag=4"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=5).count(), 'color': '#FF4081', "url": reverse("problem_judge_status") + "?flag=5"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=6).count(), 'color': '#795548', "url": reverse("problem_judge_status") + "?flag=6"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=7).count(), 'color': '#448AFF', "url": reverse("problem_judge_status") + "?flag=7"},
                {'y': ProblemMdl.JudgeStatus.objects.filter(problem=p,flag=8).count(), 'color': '#727272', "url": reverse("problem_judge_status") + "?flag=8"}
            ]
            lang_data = []
            for key, val in kernel.const.LANGUAGE_DESCRIPTION.iteritems():
                if str(key) == 'gcc':
                    ss = True
                lang_data.append({
                    'name': val,
                    'y': ProblemMdl.JudgeStatus.objects.filter(problem=p, lang=str(key)).count(),
                    'sliced': ss,
                    'selected': ss
                })
            for item in lang_data:  # 移除空白项
                if item.get('y') == 0:
                    lang_data.remove(item)

            self._result = kernel.RESTStruct(True, data={
                'flag_data': flag_data,
                'lang_data': lang_data
            })
        else:
            self._result = kernel.RESTStruct(False, msg='暂时没有评测历史')

    # ===== Protected ======

    def _save_submission(self, pid, force_judge=False):
        """
        保存提交（Control)
        :param pid: 问题ID
        :param force_judge: 是否强制开启评测
        :return:
        """

        if self._config.web_stop_judging and (not force_judge):
            return kernel.RESTStruct(False, msg='评测系统已经被管理员暂停，请稍后再试')

        problem = ProblemBodyQuery.get_problem_detail(pid)
        if problem is None:
            return kernel.RESTStruct(False, msg='题目信息不存在')

        if problem.pause_judge and (not force_judge):
            return kernel.RESTStruct(False, msg='当前题目暂停评测，请稍后再试')

        code_content = self._request.POST.get('content')
        code_lang = self._request.POST.get('lang')

        if not kernel.const.LANGUAGE_DESCRIPTION.has_key(code_lang):
            return kernel.RESTStruct(False, msg='不支持的评测语言')

        if len(code_content) < 40:
            return kernel.RESTStruct(False, msg='代码长度小于40个字符，无法进行评测')

        if str(code_lang) == 'java':
            if ('public class Main' not in code_content) or ('public static void main' not in code_content):
                 return kernel.RESTStruct(False, msg='Java语法错误：请注意，Java评测时类名必须为Main，并且类中应该定义程序入口main方法')
        else:
            if ('shutdown' in code_content) or ('system' in code_content) or ('__asm__' in code_content) or ('reboot' in code_content):
                return kernel.RESTStruct(False, msg='非法关键字：检测到您的代码可能危害评测系统。')

        # 保存代码
        status_count = ProblemMdl.JudgeStatus.objects.count()
        pack_name = str(int(status_count / 1000))         # 每1000个分开存储
        file_name = "%s.%s" % (ProblemBody.__get_upload_code_only_name(), kernel.const.SOURCE_CODE_EXTENSION[code_lang])
        full_path = "%s/%s" % (pack_name, file_name)

        storage = kernel.LocalStorage(kernel.const.USER_UPLOADCODE_DIR, pack_name)
        rel = storage.new_file(file_name, code_content)
        if not rel:
            return kernel.RESTStruct(False, msg='上传代码保存失败, 可能是系统的问题，请重试！')

        # 生成评测状态
        status = ProblemMdl.JudgeStatus()
        status.author = self._user_session.entity
        status.problem = problem
        status.timestamp = int(time.time())
        status.code_len = len(code_content)
        status.lang = code_lang
        status.code_path = full_path
        status.save()

        # 生成评测统计
        pv = ProblemMdl.ProblemVisited.objects.filter(problem=problem, author=self._user_session.entity)
        if pv.exists():
            pv = pv[0]
            pv.submissions = ProblemMdl.JudgeStatus.objects.filter(problem=problem, author=self._user_session.entity).count()
            pv.save()
        else:
            pv = ProblemMdl.ProblemVisited()
            pv.problem = problem
            pv.author = self._user_session.entity
            pv.submissions = 1
            pv.save()
        problem.total += 1
        problem.save()

        # 进入评测队列（暂时使用的队列系统）
        queue = ProblemMdl.JudgeQueue()
        queue.judge_status = status
        queue.save()

        return kernel.RESTStruct(True, data=status)

    # ===== Private =====

    def __check_permission(self):

        pass

    @staticmethod
    def __get_upload_code_only_name():
        t = str(uuid.uuid1())
        md5 = hashlib.md5()
        md5.update(t)
        return md5.hexdigest()[8:-8]


class ProblemBodyQuery(object):

    @staticmethod
    def get_problem_detail(pid, show_all=True):
        if show_all:
            pdata = ProblemMdl.Problem.objects.filter(id=pid)
        else:
            pdata = ProblemMdl.Problem.objects.filter(id=pid, is_show=True)
        if pdata.exists():
            return pdata[0]
        return None

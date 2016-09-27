# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import time
import json
import wejudge.apps.asgn.models as AsgnModel
import wejudge.kernel.general as kernel
import wejudge.kernel.problem as ProblemKernel
import AsgnProvider as Provider


class AsgnBody(ProblemKernel.ProblemBody, ProblemKernel.JudgeStatus, Provider.AsgnProvider):
    """作业展示部分"""

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'asgn'

    def problem_list(self, asgn_id):
        """作业的问题列表"""
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        permission = self._check_asgn_permission_view(asgn)
        if not permission[0]:
            return

        problem_list = []
        asgn_problem_list = {}
        require_list = {}
        asgn_problem_counter = {}
        user_solution_counter = {}
        user_solution_is_finish = {}

        if (permission[1] != -1) or (self._user_session.user_role in [2, 99]):

            asgn_problems = asgn.problemset.all()

            for asgn_problem in asgn_problems:
                pid = asgn_problem.problem.id
                problem_list.append(asgn_problem.problem)
                asgn_problem_list[pid] = asgn_problem
                if asgn_problem.require:
                    require_list[pid] = True
                asgn_problem_counter[pid] = {
                    'total': asgn_problem.submission,
                    'ac': asgn_problem.accepted,
                    'ratio': kernel.GeneralTools.ratio(asgn_problem.accepted, asgn_problem.submission)
                }
                sol = AsgnModel.Solution.objects.filter(asgn=asgn, problems=asgn_problem.problem, author=self._user_session.entity)
                if sol.exists():
                    sol = sol[0]
                    user_solution_counter[pid] = {
                        'total': sol.submission,
                        'ac': sol.accepted,
                        'ratio': kernel.GeneralTools.ratio(sol.accepted ,sol.submission)
                    }
                    if sol.accepted > 0:
                        user_solution_is_finish[pid] = True

            report = AsgnModel.StuReport.objects.filter(asgn=asgn, student=self._user_session.entity)
            if (self._user_session.user_role == 1) and (not self._is_course_assistants(asgn.course)) and (not report.exists()):
                report = AsgnModel.StuReport()
                report.asgn = asgn
                report.student = self._user_session.entity
                report.create_time = int(time.time())
                report.save()

        access_control_require = False
        if self._user_session.user_role in [2, 99]:
            if asgn.access_control.count() == 0 or asgn.access_control.count() == asgn.access_control.filter(enabled=False).count():
                access_control_require = True

        self._template_file = "asgn/body/list.html"
        self._context = {
            'asgn': asgn,
            'type': 'list',
            'problems': problem_list,
            'problem_list': problem_list,
            'asgn_problems': asgn_problem_list,
            'require_list': require_list,
            'asgn_problem_counter': asgn_problem_counter,
            'user_solution_counter': user_solution_counter,
            'user_solution_is_finish': user_solution_is_finish,
            'access_control_require': access_control_require,
            'permission': permission
        }

    def show_asgn_problem(self, asgn_id, problem_id):
        """
        题目展示
        """
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        permission = self._check_asgn_permission_view(asgn)
        if not permission[0]:
            return

        ap = asgn.problemset.filter(problem__id=problem_id)
        if not ap.exists():
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_PROBLEM_NOT_FOUND
        ap = ap[0]

        if not super(AsgnBody, self).show_problem(problem_id, True):            # 调用上级题目展示
            return

        problem_list = self._get_problem_list(asgn)
        language_provider = kernel.GeneralTools._get_langauage_limit(asgn.lang, ap.lang)

        if self._user_session.user_role == 1:
            sol = AsgnModel.Solution.objects.filter(asgn=asgn, problems=ap.problem, author=self._user_session.entity)
            if not sol.exists():
                sol = AsgnModel.Solution()
                sol.asgn = asgn
                sol.problems = ap.problem
                sol.author = self._user_session.entity
                sol.start_time = int(time.time())
                sol.save()

        self._context.update({
            'asgn': asgn,
            'problem_list': problem_list,
            'language_provider': language_provider,
            'permission': permission
        })
        self._template_file = "asgn/body/problem.html"

    def my_status_list(self, aid, pid):
        """(AJAX WebPage)在这个作业里某题我的评测记录"""
        if not self._check_login(True):
            return
        asgn = self._get_asgn_detail(aid)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都
        jst = asgn.judge_status.filter(problem__id=pid, author=self._user_session.entity).order_by('-id')
        count = jst.count()
        if count > 20:
            count = 20
        jdugestatus = jst.all()[:count]
        self._template_file = 'problem/status/list_body.html'
        self._context = {
            'asgn': asgn,
            'status_list': jdugestatus
        }

    def asgn_status_list(self, asgn_id, page=1, limit=50):
        """作业里的评测记录"""
        asgn = self._get_asgn_detail(asgn_id)
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        permission = self._check_asgn_permission_view(asgn)
        if not permission[0]:
            return

        jst, dst = self._get_status_list(asgn.judge_status)
        count = jst.count()
        pager = kernel.PagerProvider(count, limit, page, 'asgn_status_list', 11, self._request.GET, asgn_id)
        if count > 0:
            jdugestatus = jst.all()[pager.start_idx: pager.start_idx + limit]
        else:
            jdugestatus = []
        self._template_file = "asgn/body/status.html"
        self._context = {
            'asgn': asgn,
            'type': 'status',
            'problem_list': self._get_problem_list(asgn),
            'pager': pager.render(),
            'status_list': jdugestatus,
            'permission': permission
        }
        self._context.update(dst)

    def asgn_rank_list(self, asgn_id):
        """排行榜子系统"""
        asgn = self._get_asgn_detail(asgn_id)
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        permission = self._check_asgn_permission_view(asgn)
        if not permission[0]:
            return

        rank_data = self._asgn_rank_list_counter(asgn)
        try:
            rank_data = json.loads(rank_data)
        except:
            rank_data = None

        self._template_file = "asgn/body/ranklist.html"
        self._context = {
            'asgn': asgn,
            'type': 'ranklist',
            'problem_list': self._get_problem_list(asgn),
            'permission': permission,
            'rank_data': rank_data
        }

    def asgn_answer_view(self, asgn_id):
        """参考答案页面"""
        asgn = self._get_asgn_detail(asgn_id)
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        permission = self._check_asgn_permission_view(asgn)
        if not permission[0]:
            return

        problem_list = self._get_problem_list(asgn)
        demos = []
        if permission[1] >= 1:
            for problem in problem_list:
                try:
                    demo = json.loads(problem.demo_code)
                    demos.append({"pid": problem.id, 'pname': problem.title, 'code': demo.get('content', None), 'lang': demo.get('lang', '')})
                except:
                    demos.append({"pid": problem.id, 'pname': problem.title, 'code': None})

        self._template_file = "asgn/body/answer.html"
        self._context = {
            'asgn': asgn,
            'type': 'answer',
            'problem_list': problem_list,
            'permission': permission,
            'demos': demos
        }

    def save_asgn_submission(self, asgn_id, problem_id):
        """提交代码评测"""
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        asgn_problem = asgn.problemset.filter(problem__id=problem_id)
        if not asgn_problem.exists():
            self._result = kernel.RESTStruct(False, msg='这个作业没有设置这道题目')
            return
        asgn_problem = asgn_problem[0]

        flag, dec = self._check_asgn_permission(asgn)
        if flag != 0:
            if flag == -1:
                self._result = kernel.RESTStruct(False, msg='对不起，作业还没开放')
                return
            elif flag == 1:
                self._result = kernel.RESTStruct(False, msg='对不起，作业提交已经结束')
                return

        proc_result = self._save_submission(problem_id)     # 调用父类设置好的方法

        if proc_result.flag is True:                        # 如果父类方法处理成功
            status = proc_result.data
            status.callback = json.dumps({'provider': 'asgn', 'id': asgn.id})
            status.save()
            asgn.judge_status.add(status)
            asgn.save()
            sol = AsgnModel.Solution.objects.filter(asgn=asgn, problems=asgn_problem.problem, author=self._user_session.entity)
            if not sol.exists():
                sol = AsgnModel.Solution()
                sol.asgn = asgn
                sol.problems = asgn_problem.problem
                sol.author = self._user_session.entity
                sol.start_time = int(time.time())
                sol.save()
            else:
                sol = sol[0]
            sol.judge_status.add(status)
            sol.submission += 1
            sol.save()
            asgn_problem.submission += 1
            asgn_problem.save()

            proc_result.data = status.id
        else:
            proc_result.data = None

        self._result = proc_result

    def show_report(self, asgn_id, author_id):
        """
        实验报告展示页面
        :param asgn_id:
        :param author_id:
        :return:
        """
        asgn = self._get_asgn_detail(asgn_id)
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        permission = self._check_asgn_permission_view(asgn)

        if not self._is_course_assistants(asgn.course):
            if not permission[0]:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_ASGN_REPORT_NO_USE
                return

        report = AsgnModel.StuReport.objects.filter(asgn=asgn, student__id=author_id)
        if str(self._user_session.user_id) == str(author_id):
            if report.exists():
                report = report[0]
                """
                if permission[1] == 0:
                    self._report_count_by_solutions(asgn, report)
                """
            else:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_ASGN_USER_REPORT_NOT_FOUND
                return
        else:
            if report.exists():
                report = report[0]
            else:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_ASGN_USER_REPORT_NOT_FOUND
                return

        score_list = {}
        asgn_problems = asgn.problemset.all()
        for ap in asgn_problems:
            score_list[ap.problem.id] = ap.score

        self._template_file = 'asgn/body/report.html'
        self._context = {
            'asgn': asgn,
            'type': 'report',
            'problem_list': self._get_problem_list(asgn),
            'permission': permission,
            'report': report,
            'score_list': score_list,
            'solutions': asgn.solution_set.filter(author_id=author_id)
        }

    def save_impression(self, asgn_id):
        """保存评测详情"""
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        flag, dec = self._check_asgn_permission(asgn)
        if flag != 0:
            if flag == -1:
                self._result = kernel.RESTStruct(False, msg='对不起，作业还没开放')
            elif flag == 1:
                self._result = kernel.RESTStruct(False, msg='对不起，作业提交已经结束')
            return

        report = AsgnModel.StuReport.objects.filter(asgn=asgn, student=self._user_session.entity)
        if not report.exists():
            self._result = kernel.RESTStruct(False, msg='你还没有生成实验报告')
            return
        report = report[0]

        impression = self._request.POST.get('impression', '')
        report.impression = impression
        report.modify_time = int(time.time())
        report.save()
        self._result = kernel.RESTStruct(True)


